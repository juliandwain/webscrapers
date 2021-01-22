# -*- coding: utf-8 -*-

__doc__ = """

"""

import pathlib
from typing import Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from .wait import element_wait

__all__ = [
    "Webdriver",
]


class Webdriver:
    """The `Webdriver` class.
    """

    def __init__(self, url: str, headless: bool = True) -> None:
        """Init the class.

        Parameters
        ----------
        url : str
            The url which should be loaded.
        headless : bool, optional
            Determine if the browser should be executed
            without opening a window, by default True.

        """
        # define the path to the driver
        self._path = pathlib.Path("./scraper/drivers/geckodriver.exe")
        # set some options using the built-in Options class
        options = Options()
        options.headless = headless
        # define the engine, i.e. the browser to be used
        self._engine = webdriver.Firefox(
            options=options, executable_path=self._path)
        # save the url
        self._url = url
        # define a strategy dictionary
        self._strategy_dic = {
            "id": By.ID,
            "xpath": By.XPATH,
            "link_text": By.LINK_TEXT,
            "partial_link_test": By.PARTIAL_LINK_TEXT,
            "name": By.NAME,
            "tag_name": By.TAG_NAME,
            "class_name": By.CLASS_NAME,
            "css_selector": By.CSS_SELECTOR,
        }
        # define a timeout
        self._timeout = 10

    def __enter__(self) -> None:
        """Load the `url` given when entering.
        """
        self.load_url()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._engine.quit()

    @property
    def engine(self) -> webdriver.Firefox:
        """Get the current engine.

        Returns
        -------
        webdriver
            The current engine.

        """
        return self._engine

    @property
    def url(self) -> str:
        """Get the current `url`.

        Returns
        -------
        str
            The current url.

        """
        return self._url

    @url.setter
    def url(self, val: str) -> None:
        """Set a new url.

        Parameters
        ----------
        val : str
            The new url.

        """
        self._url = val

    def find_object(
            self,
            by_strat: Optional[str],
            idx: Union[list, int, None],
            **kwargs: dict):
        """Find all <object></object> html elements in the given html page or in the given webelement.

        Parameters
        ----------
        by_strat : str or None
            Determine a by strategy by which the given element
            should be searched for value.
            Can be one of the following:
            * "id"
            * "xpath"
            * "link_text"
            * "partial_link_test"
            * "name"
            * "tag_name"
            * "class_name"
            * "css_selector"

        idx : list or int or None
            The index/number of the html element which you want to access.
            If set to None, all elements are examined.

        Other Parameters
        ----------------
        element : selenium.webdriver.webelement
            The webelement which should be searched.
        val : str
            The value of the table element corresponding to the type
            of strategy chosen, see [1].
        condition_type : str
            See the docs for element_wait().

        Returns
        -------
        list or selenium.webdriver.webelement
            A list containing the selenium.webdriver.webelement s. If the index, i.e. `idx` is set to a single value,
            i.e. an integer, then the webdriver element is directly returned.

        Notes
        -----
        This function extracts all content in the table:

        .. highlight:: html
        .. code-block:: html

            <object>
                content
            </object>

        If no by strategy is given, the default is set to CSS_SELECTOR.
        If a specific element is chosen, the val parameter has to be adapted to the by strategy, which is set to
        CSS_SELECTOR if set to None, thus the val parameter has to be as CSS_SELECTOR.
        If no kwargs are given, the whole html element is searched for <object></object>.

        References
        ----------
        .. [1] https://selenium-python.readthedocs.io/locating-elements.html

        """
        by = self._strategy_dic.get(by_strat, By.CSS_SELECTOR)
        element = kwargs.get("element", self._engine)
        val = kwargs.get("val", None)
        condition_type = kwargs.get("condition_type", "presence_all")

        if val is None:
            # wrong input combinations are prevented by calling self._browser if the value is set to None
            html = element_wait(element=self._engine, time=self._timeout, by=By.CSS_SELECTOR, val="html",
                                condition_type="presence")
            # search the element for the self._get_html_name()
            obj = html.find_elements(by)
        else:
            obj = element_wait(element=element, time=self.timeout,
                               by=by, val=val, condition_type=condition_type)

        helper = np.atleast_1d(obj)
        if idx is not None:
            arr = np.atleast_1d(idx)  # transform to numpy array
        else:
            arr = np.arange(0, len(helper))

        arrays = helper[arr]

        if arrays.shape[0] == 1:
            return arrays[0]
        else:
            return arrays.tolist()

    def load_url(self) -> None:
        """Load to given url.

        Notes
        -----
        This method has to be called before making any other operations
        on the webpage, otherwise the url will not be
        loaded into to driver object.

        """
        self._engine.get(self._url)
