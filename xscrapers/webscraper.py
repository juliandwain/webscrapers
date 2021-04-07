# -*- coding: utf-8 -*-

__doc__ = """This module implements the webscraper.
"""

import functools
import http.client
import itertools
import logging
import os
from concurrent.futures import ThreadPoolExecutor  # ,ProcessPoolExecutor
from typing import List, Optional, Union

import requests
from bs4 import BeautifulSoup, SoupStrainer
from bs4.dammit import EncodingDetector
from fake_useragent import UserAgent

from . import LOG_DIR
from ._base import DATA_OBJECT, Scraper

# set up the logging configuration
http.client.HTTPConnection.debuglevel = 0
LOG_FILE = LOG_DIR / f"{__name__.split('.')[-1]}.log"

REQUESTS_LOG = logging.getLogger("requests.packages.urllib3")
REQUESTS_LOG.setLevel(logging.DEBUG)
REQUESTS_LOG.propagate = True

FILE_HANDLER = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
FILEFORMAT = logging.Formatter(
    "%(asctime)s:[%(threadName)-12.12s]:%(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
FILE_HANDLER.setFormatter(FILEFORMAT)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.WARNING)
STREAMFORMAT = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
STREAM_HANDLER.setFormatter(STREAMFORMAT)

REQUESTS_LOG.addHandler(FILE_HANDLER)
REQUESTS_LOG.addHandler(STREAM_HANDLER)

logging.basicConfig(handlers=[FILE_HANDLER, STREAM_HANDLER])
logging.getLogger().setLevel(logging.WARNING)

STATUS_CODES = {
    100: "Informational Responses",
    200: "Success",
    300: "Redirection",
    400: "Client Errors",
    500: "Server Errors",
}

RESPONSE_OBJECT = Union[None, requests.Response,
                        List[requests.Response], requests.exceptions.RequestException]


def callback(
    res: requests.Response,
    *args,
    **kwargs
) -> requests.Response:
    """Callback function.

    Parameters
    ----------
    res : requests.Response
        A response object.

    Returns
    -------
    requests.Response
        A request.Response object.

    """
    # indicate that the callback funtion was called
    res.hook_called = True
    if args:
        raise AssertionError(f"Have a look at what is in {args}")
    msg = f"\n----- REPORT START -----\n" \
          f"URL: {res.url}\n" \
          f"Time: {res.elapsed.total_seconds():.3f}s\n" \
          f"Encoding: {res.encoding}\n" \
          f"Reason: {res.reason}\n" \
          f"Status Code: {res.status_code}\n" \
          f"Certificate: {kwargs.get('cert', None)}\n" \
          f"----- REPORT END -----\n"
    REQUESTS_LOG.debug(msg)
    return res


class Webscraper(Scraper):
    """The Webscraper class.

    Note that the class saves only the results from the last request made,
    i.e., when making a combination of GET and PUT request, only the last
    results is saved in the class' attributes.

    """

    def __init__(
        self,
        parser: str,
        verbose: bool = False,
    ) -> None:
        """Init the class.

        Parameters
        ----------
        parser : str
            The parser to be used. Can either be:

            * "html.parser"
            * "lxml"

        verbose : bool
            Determine whether the output should be written to the log file,
            by default False.

        References
        ----------
        [1] https://2.python-requests.org/en/master/

        """
        super().__init__()
        self._parser = parser
        self._verbose = verbose

        self._max_threads = os.cpu_count()*2 - 4
        self._max_processes = os.cpu_count() - 2

        self._user_agent = UserAgent()
        self._headers = {"User-Agent": self._user_agent.random}
        self._sess = requests.Session()
        if self._verbose:
            self._sess.hooks["response"].append(callback)

        # initialize the response and data attributes
        self._res = None
        self._data = None

        # define a dictionary which contains values to check which type of
        # http request has been made
        self._http_request = {
            "DELETE": False,
            "GET": False,
            "PATCH": False,
            "POST": False,
            "PUT": False,
            "OPTIONS": False,
        }

    def __str__(self) -> str:
        if isinstance(self._url, list):
            msg = ""
            for url in self._url:
                msg += url + "\n"
        elif isinstance(self._url, str):
            msg = self._url + "\n"
        else:
            msg = "No url given."
        return msg

    @property
    def res(self) -> RESPONSE_OBJECT:
        """The response object.

        Returns
        -------
        RESPONSE_OBJECT
            None if not yet set, the/all response object(s),
            or the error thrown.

        """
        return self._res

    @property
    def data(self) -> DATA_OBJECT:
        """The data object.

        Returns
        -------
        DATA_OBJECT
            The data object.

        """
        return self._data

    @data.setter
    def data(self, val: DATA_OBJECT) -> None:
        """Set a new data object.

        Parameters
        ----------
        val : DATA_OBJECT
            The new value for data.

        """
        self._data = val

    @functools.singledispatchmethod
    def _request(
        self,
        url: Union[str, List[str]],
        method: str,
        kwargs: dict,
    ) -> None:
        """Make a request specified by ``method``.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url to which the request should be made.
        method : str
            The method which should be applied. Can be

            * "DELETE"
            * "GET"
            * "PATCH"
            * "POST"
            * "PUT"
            * "OPTIONS"

        kwargs : dict
            A dictionary containing keyword arguments which are passed to
            the respective method chosen, see [1].

        Raises
        ------
        NotImplementedError
            If ``url`` is neither of type str nor list.

        Notes
        -----
        The ``kwargs`` parameter are specified in the respective method
        within this class.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        raise NotImplementedError(
            f"Parameter url is neither of type {str} nor {list}, it is of type {type(url)}.")

    @_request.register
    def _(
        self,
        url: str,
        method: str,
        kwargs: dict,
    ) -> RESPONSE_OBJECT:
        """Make a request to a single url.

        Parameters
        ----------
        url : str
            The url which should be accessed.
        method : str
            The method which should be applied.
        kwargs : dict
            See the documentation for ``self._request`` method.

        Returns
        -------
        RESPONSE_OBJECT
            The reponse object.

        """
        # save the url to the data class
        self._url = url
        with self._sess as sess:
            try:
                res = sess.request(
                    method.upper(),
                    url,
                    headers=self._headers,
                    timeout=self._timeout,
                    **kwargs,
                )
                if not res.ok:  # check if no bad response is returned
                    REQUESTS_LOG.warning(
                        f"Response for {url} failed!\nResponse status code: {res.status_code}.")
                if self._verbose:
                    REQUESTS_LOG.debug("Total Time: %3f s",
                                       res.elapsed.total_seconds())
            except requests.exceptions.RequestException as e:
                REQUESTS_LOG.warning(
                    f"Sending a {method.upper()} request to {url} has failed!\nThe exception thrown is {e}")
                res = e
        # set the attribute
        self.__setattr__("_res", res)
        self._http_request[method.upper()] = True
        return res

    @_request.register
    def _(
        self,
        url: list,
        method: str,
        kwargs: dict,
    ) -> None:
        """Make a request to multiple urls.

        Parameters
        ----------
        url : list
            The urls which should be accessed.
        method : str
            The method which should be applied.
        kwargs : dict
            See the documentation for ``self._request`` method.

        Notes
        -----
        This function uses multithreading since loading multiple URLs is an I/O
        bound task. For this, a computer and system dependent maximum number
        of threads have to be given.

        """
        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            responses = list(executor.map(
                self._request,
                url,
                itertools.repeat(method),
                itertools.repeat(kwargs),
            ))
            # wait until all threads are finished
            executor.shutdown(wait=True)
        # filter out Response >=[400] and exceptions
        _res = []
        _urls = []
        for i, res in enumerate(responses):
            # filter out errors
            if isinstance(res, requests.exceptions.RequestException):
                continue
            else:
                if res.ok:
                    _res.append(res)
                    _urls.append(url[i])
                else:  # filter out bad responses
                    continue
        self._url = _urls
        # set the attribute
        self.__setattr__("_res", _res)
        self._http_request[method.upper()] = True

    def get(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make a GET request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a GET request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "GET"
        self._request(url, method, kwargs)

    def put(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make a PUT request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a PUT request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "PUT"
        self._request(url, method, kwargs)

    def delete(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make a DELETE request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a DELETE request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "DELETE"
        self._request(url, method, kwargs)

    def head(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make a HEAD request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a HEAD request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "HEAD"
        self._request(url, method, kwargs)

    def options(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make an OPTIONS request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a OPTIONS request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "OPTIONS"
        self._request(url, method, kwargs)

    def post(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make a POST request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a POST request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "POST"
        self._request(url, method, kwargs)

    def patch(
        self,
        url: Union[str, List[str]],
        kwargs: dict = {},
    ) -> None:
        """Make a PATCH request.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url(s) to which a PATCH request should be made.
        kwargs : dict, optional
            A dictionary containing arguments described in [1],
            by default {}.

        References
        ----------
        [1] https://docs.python-requests.org/en/latest/api/

        """
        method = "PATCH"
        self._request(url, method, kwargs)

    def parse(
        self,
        name: Optional[str] = None,
        **kwargs: dict,
    ) -> None:
        """Parse a single or a list of response objects.

        Parameters
        ----------
        name : Optional[str]
            Parse only a part of the document specified by a name
            (see the documentation for ``_parse_response()``),
            by default None.

        Other Parameters
        ----------------
        Parameters passed into the ``SoupStrainer`` object, the same as for
        the find_all method of BS4, see the documentation for 
        ``_parse_response()``.

        Raises
        ------
        AssertionError
            If ``self.load`` has not been called before calling this method.

        Notes
        -----
        The parsed response objects are stored in the ``data`` attribute of the
        class which has type Union[BeautifulSoup, List[BeautifulSoup]]
        depending on the input the same output is returned with parsed htmls.

        """
        if not self._http_request["GET"]:
            raise AssertionError(
                f"Expected {self.get} to be called before calling {self.parse}.")
        if isinstance(self._res, list):
            obj = []
            for response in self._res:
                obj.append(self._parse_response(response, name, **kwargs))
            # with ProcessPoolExecutor(max_workers=self._max_processes) as executor:
            #     obj = list(executor.map(self._parse_response, res))
        else:
            obj = self._parse_response(self._res, name, **kwargs)
        self.__setattr__("_data", obj)

    def _parse_response(
        self,
        res: requests.Response,
        name: Optional[str],
        **kwargs: dict,
    ) -> BeautifulSoup:
        """Parse a single response object.

        Parameters
        ----------
        res : requests.Response
            The response to be parsed.
        name : Optional[str]
            Parse only a part of the document specified by a ``name``
            (see [1]), by default None.

        Other Parameters
        ----------------
        Parameters passed into the ``SoupStrainer`` object, the same as for
        the ``find_all`` method of BS4, see [2].

        Returns
        -------
        BeautifulSoup
            The response as Beautifulsoup object.

        Notes
        -----
        This function takes in a string as name which is wrapped
        into a ``SoupStrainer`` object.

        References
        ----------
        [1] https://www.crummy.com/software/BeautifulSoup/bs4/doc/#soupstrainer
        [2] https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all

        """
        # deterime the correct encoding
        http_encoding = res.encoding if "charset" in res.headers.get(
            "content-type", "").lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(
            res.content, is_html=True)
        encoding = html_encoding or http_encoding
        # parse the document
        parse_only = SoupStrainer(name, **kwargs)
        obj = BeautifulSoup(
            res.content,
            self._parser,
            from_encoding=encoding,
            parse_only=parse_only,
        )
        return obj
