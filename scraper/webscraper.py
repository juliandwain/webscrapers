# -*- coding: utf-8 -*-

__doc__ = """This module implements the webscraper.
"""

import http.client
import pathlib
import logging
from concurrent.futures import ThreadPoolExecutor

import requests
from fake_useragent import UserAgent

__all__ = [
    "Webscraper",
]

# set the debug level
http.client.HTTPConnection.debuglevel = 1
LOG_FILE = pathlib.Path(f"./scraper/{__name__}.log")

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
REQUESTS_LOG = logging.getLogger("requests.packages.urllib3")
REQUESTS_LOG.setLevel(logging.DEBUG)
REQUESTS_LOG.propagate = True

FILE_HANDLER = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
FORMATTER = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
FILE_HANDLER.setFormatter(FORMATTER)
REQUESTS_LOG.addHandler(FILE_HANDLER)


def _load_url(url: str) -> requests.Response:
    """Load a single url and return the corresponding response.

    Parameters
    ----------
    url : str
        The url to be loaded.

    Returns
    -------
    res : requests.Response
        The response from the webbrowser with the current url.

    Notes
    -----
    This function is used for parallelly loading url responses.

    """

    user_agent = UserAgent()
    headers = {"User-Agent": user_agent.random}
    sess = requests.Session()
    with sess:
        res = sess.get(url, headers=headers)
    return res


def _load_urls(urls: list, max_threads: int) -> list:
    """Load a list of urls to response objects.

    Parameters
    ----------
    urls : list
        A list of urls to be loaded with the session objects.
    max_threads : int
        Maximum number of threads to use.

    Returns
    -------
    list
        A list of requests.Response objects corresponding to the urls given.

    Notes
    -----
    This function uses multithreading since loading multiple URLs is an I/O
    bound task. For this, a computer and system dependent maximum number
    of threats have to be given.

    """

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        responses = list(executor.map(_load_url, urls))
        # wait until all threats are finished
        executor.shutdown(wait=True)
    return responses


class Webscraper:
    """[summary]
    """

    def __init__(self, parser: str) -> None:
        self._parser = parser

        self._max_threads = 4

        self._user_agent = UserAgent()
        self._headers = {"User-Agent": self._user_agent.random}
        self._sess = requests.Session()

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
            res = self._sess.get(url, headers=self._headers)
        return res

    def load_urls(self, urls: list) -> list:
        """Load a list of urls.

        Parameters
        ----------
        urls : list
            A list of string urls to be loaded.

        Returns
        -------
        list
            A list of response objects corresponding to the urls.

        Notes
        -----
        This function is based on the _load_urls function
        provided within this module.

        """
        responses = _load_urls(urls, self._max_threads)
        return responses
