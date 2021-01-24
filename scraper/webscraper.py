# -*- coding: utf-8 -*-

__doc__ = """This module implements the webscraper.
"""

import http.client
import json
import logging
import os
import pathlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Union

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm

__all__ = [
    "Webscraper",
]

# set up the logging configuration
http.client.HTTPConnection.debuglevel = 0
LOG_FILE = pathlib.Path(f"./scraper/{__name__.split('.')[-1]}.log")

REQUESTS_LOG = logging.getLogger("requests.packages.urllib3")
REQUESTS_LOG.setLevel(logging.DEBUG)
REQUESTS_LOG.propagate = True

FILE_HANDLER = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
FORMATTER = logging.Formatter(
    "%(asctime)s:[%(threadName)-12.12s]:%(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
FILE_HANDLER.setFormatter(FORMATTER)
REQUESTS_LOG.addHandler(FILE_HANDLER)
logging.basicConfig(handlers=[FILE_HANDLER])
logging.getLogger().setLevel(logging.DEBUG)


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
    # save json data if available
    try:
        res.data = res.json()
    except json.decoder.JSONDecodeError:
        res.data = None
    if args:
        raise AssertionError(f"Have a look at what is in {args}")
    msg = f"----- REPORT START -----\n" \
          f"URL: {res.url}\n" \
          f"Time: {res.elapsed.total_seconds():.3f}s\n" \
          f"Encoding: {res.encoding}\n" \
          f"Reason: {res.reason}\n" \
          f"Status Code: {res.status_code}\n" \
          f"Certificate: {kwargs.get('cert', None)}\n" \
          f"----- REPORT END -----\n"
    print(msg)
    return res


class Webscraper:
    """[summary]
    """

    def __init__(self, parser: str) -> None:
        """Init the class.

        Parameters
        ----------
        parser : str
            The parser to be used. Can either be:

            * "html.parser"
            * "lxml"

        """
        self._parser = parser

        self._max_threads = 8
        self._max_processes = os.cpu_count() - 2

        self._user_agent = UserAgent()
        self._headers = {"User-Agent": self._user_agent.random}
        self._sess = requests.Session()
        self._sess.hooks["response"].append(callback)
        self._timeout = 15

    def load_url(self, url: str) -> requests.Response:
        """Load a single url.

        Parameters
        ----------
        url : str
            The url to be loaded.

        Returns
        -------
        requests.Response
            The corresponding response object

        """
        with self._sess:
            res = self._sess.get(
                url, headers=self._headers, timeout=self._timeout)
        return res

    def load_urls(self, urls: list) -> list:
        """Load a list of urls to response objects.

        Parameters
        ----------
        urls : list
            A list of urls to be loaded with the session objects.

        Returns
        -------
        list
            A list of requests.Response objects corresponding to the urls given.

        Notes
        -----
        This function uses multithreading since loading multiple URLs is an I/O
        bound task. For this, a computer and system dependent maximum number
        of threads have to be given.

        """
        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            responses = list(executor.map(self.load_url, urls))
            # wait until all threats are finished
            executor.shutdown(wait=True)
        return responses

    def parse(
        self,
        res: Union[list, requests.Response]
    ) -> Union[list, requests.Response]:
        """Parse a single or a list of response objects.

        Parameters
        ----------
        res : Union[list, requests.Response]
            The response object(s).

        Returns
        -------
        Union[list, requests.Response]
            Depending on the input the same output is returned with parsed
            htmls.

        """
        if isinstance(res, list):
            obj = []
            for response in tqdm(res):
                obj.append(BeautifulSoup(response.content, self._parser))
            # with ProcessPoolExecutor(max_workers=self._max_processes) as executor:
            #     obj = list(executor.map(BeautifulSoup.__init__, [
            #                re.content for re in res], len(res)*[self._parser]))
        else:
            obj = BeautifulSoup(res.content, self._parser)
        return obj
