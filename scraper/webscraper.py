# -*- coding: utf-8 -*-

__doc__ = """This module implements the webscraper.
"""

import http.client
import logging
import os
from concurrent.futures import ThreadPoolExecutor  # ,ProcessPoolExecutor
from typing import List, Optional, Union

import requests
from bs4 import BeautifulSoup
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


def callback(res: requests.Response, *args, **kwargs) -> requests.Response:
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
    """

    def __init__(
        self,
        parser: str,
        verbose: bool = False,
        get_params: Optional[dict] = None,
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
        get_params : Optional[dict]
            A dictionary containing parameters for the GET request,
            by default None. See [1].

        References
        ----------
        [1] https://2.python-requests.org/en/master/

        """
        super().__init__()
        self._parser = parser
        self._verbose = verbose
        if get_params:
            self._get_params = get_params
        else:
            self._get_params = {}

        self._max_threads = os.cpu_count()*2 - 4
        self._max_processes = os.cpu_count() - 2

        self._user_agent = UserAgent()
        self._headers = {"User-Agent": self._user_agent.random}
        self._sess = requests.Session()
        if self._verbose:
            self._sess.hooks["response"].append(callback)
        self._timeout = 15

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

    def get(
        self,
        url: Union[str, List[str]],
    ) -> None:
        """Make a GET request to a single or multiple urls.

        Parameters
        ----------
        url : Union[str, List[str]]
            The url or list of urls to be loaded.

        Raises
        ------
        AssertionError
            If `url` is neither of type `str` nor of type `list`.

        """
        # save the url to the data class
        self._url = url
        if isinstance(self._url, str):
            self._url = self._url.strip()
            res = self._load_url(self._url)
        elif isinstance(self._url, list):
            self._url = [ur.strip() for ur in self._url]
            res = self._load_urls(self._url)
        else:
            raise AssertionError(
                f"Parameter url is neither of type {str} nor {list}, it is of type {type(url)}.")
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["GET"] = True

    def _load_url(
        self,
        url: str,
    ) -> Union[requests.Response, requests.exceptions.RequestException]:
        """Load a single url.

        Parameters
        ----------
        url : str
            The url to be loaded.

        Returns
        -------
        Union[requests.Response, requests.exceptions.RequestException]
            The corresponding response object. If the request fails
            for some reason, the error itself is returned.

        """
        with self._sess as sess:
            try:
                res = sess.get(
                    url,
                    headers=self._headers,
                    timeout=self._timeout,
                    **self._get_params,
                )
                if not res.ok:  # check if no bad response is returned
                    REQUESTS_LOG.warning(
                        f"Response for {url} failed!\nResponse status code: {res.status_code}.")
                if self._verbose:
                    REQUESTS_LOG.debug("Total Time: %3f s",
                                       res.elapsed.total_seconds())
            except requests.exceptions.RequestException as e:
                REQUESTS_LOG.warning(
                    f"Sending a GET request to {url} has failed!\nThe exception thrown is {e}")
                res = e
        return res

    def _load_urls(
        self,
        urls: List[str],
    ) -> List[requests.Response]:
        """Load a list of urls to response objects.

        Parameters
        ----------
        urls : list
            A list of urls to be loaded with the session objects.

        Returns
        -------
        List[requests.Response]
            A list of requests.Response objects corresponding to the urls given.

        Notes
        -----
        This function uses multithreading since loading multiple URLs is an I/O
        bound task. For this, a computer and system dependent maximum number
        of threads have to be given.

        """
        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            responses = list(executor.map(self._load_url, urls, chunksize=8))
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
                    _urls.append(urls[i])
                else:  # filter out bad responses
                    continue
        self._url = _urls
        return _res

    def put(
        self,
        url: str
    ) -> None:
        """Make a PUT request to a single url.

        Parameters
        ----------
        url : str
            The url to which a PUT request should be made.

        """
        self._url = url
        with self._sess as sess:
            res = sess.put(url)
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["PUT"] = True

    def delete(
        self,
        url: str
    ) -> None:
        """Make a DELETE request to a single url.

        Parameters
        ----------
        url : str
            The url to which a DELETE request should be made.

        """
        self._url = url
        with self._sess as sess:
            res = sess.delete(url)
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["DELETE"] = True

    def head(
        self,
        url: str
    ) -> None:
        """Make a HEAD request to a single url.

        Parameters
        ----------
        url : str
            The url to which a HEAD request should be made.

        """
        self._url = url
        with self._sess as sess:
            res = sess.head(url)
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["HEAD"] = True

    def options(
        self,
        url: str
    ) -> None:
        """Make an OPTIONS request to a single url.

        Parameters
        ----------
        url : str
            The url to which an OPTIONS request should be made.

        """
        self._url = url
        with self._sess as sess:
            res = sess.options(url)
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["OPTIONS"] = True

    def post(
        self,
        url: str,
        payload: dict = {},
    ) -> None:
        """Make a POST request to a single url.

        Parameters
        ----------
        url : str
            The url to which a POST request should be made.
        payload : dict, optional
            The data which should be delivered with the post request,
            by default {}.

        """
        self._url = url
        with self._sess as sess:
            res = sess.post(
                url,
                data=payload
            )
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["POST"] = True

    def patch(
        self,
        url: str,
    ) -> None:
        """Make a PATCH request to a single url.

        Parameters
        ----------
        url : str
            The url to which a PATCH request should be made.

        """
        self._url = url
        with self._sess as sess:
            res = sess.patch(url)
        # set the attribute
        setattr(self, "_res", res)
        self._http_request["PATCH"] = True

    def parse(self) -> None:
        """Parse a single or a list of response objects.

        Raises
        ------
        AssertionError
            If `self.load` has not been called before calling this method.

        Notes
        -----
        The parsed response objects are stored in the `data` attribute of the
        class which has type Union[BeautifulSoup, List[BeautifulSoup]]
        depending on the input the same output is returned with parsed htmls.

        """
        if not self._http_request["GET"]:
            raise AssertionError(
                f"Expected {self.get} to be called before calling {self.parse}.")
        if isinstance(self._res, list):
            obj = []
            for response in self._res:
                obj.append(self._parse_response(response))
            # with ProcessPoolExecutor(max_workers=self._max_processes) as executor:
            #     obj = list(executor.map(self._parse_response, res))
        else:
            obj = self._parse_response(self._res)
        setattr(self, "_data", obj)

    def _parse_response(
        self,
        res: requests.Response
    ) -> BeautifulSoup:
        """Parse a single response object.

        Parameters
        ----------
        res : requests.Response
            The response to be parsed.

        Returns
        -------
        BeautifulSoup
            The response as Beautifulsoup object.

        """
        http_encoding = res.encoding if "charset" in res.headers.get(
            "content-type", "").lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(
            res.content, is_html=True)
        encoding = html_encoding or http_encoding
        obj = BeautifulSoup(res.content, self._parser,
                            from_encoding=encoding)
        return obj
