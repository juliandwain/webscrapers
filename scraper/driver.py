# -*- coding: utf-8 -*-

__doc__ = """

"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pathlib

__all__ = [
    "Webdriver",
]


class Webdriver:

    def __init__(self, url: str, headless: bool = True) -> None:
        # define the path to the driver
        self._path = pathlib.Path("./scraper/drivers/geckodriver.exe")
        # set some options using the built-in Options class
        options = Options()
        options.headless = headless
        # define the engine, i.e. the browser to be used
        self._engine = webdriver.Firefox(
            options=options, executable_path=self._path)
        self._url = url

    def __enter__(self) -> None:
        self.load_url()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._engine.quit()

    @property
    def engine(self) -> webdriver:
        return self._engine

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, val: str):
        self._url = val

    def load_url(self) -> None:
        """Load to given url to the self._browser object.

        Notes
        -----
        This method has to be called before making any other operations
        on the webpage, otherwise the url will not be
        loaded into to driver object.

        """
        self._engine.get(self._url)
