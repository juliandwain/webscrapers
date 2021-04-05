# -*- coding: utf-8 -*-

__doc__ = """
"""

from typing import Callable, Dict, List

import pandas as pd
from bs4 import BeautifulSoup, Tag

from ..webscraper import DATA_OBJECT, Webscraper

__all__ = [
    "Parser",
]


def _get_tables(
    tables: list,
) -> List[pd.DataFrame]:
    """Get <table></table> elements as dataframe.

    Parameters
    ----------
    tables : list
        The list of html tables.

    Returns
    -------
    List[pd.DataFrame]
        A list of pandas DataFrames containing the tables.

    """
    df = []
    for table in tables:
        _df = pd.read_html(
            table.prettify(),
            flavor="bs4",
        )[0]
        df.append(_df)
    return df


def _get_href(
    a: list,
    url: str
) -> List[str]:
    """Get href from <a></a> elements as list.

    Parameters
    ----------
    a : list
        The list of html a objects.
    url : str
        The url which is loaded.

    Returns
    -------
    List[str]
        A list of strings containing the urls on the webpage.

    Notes
    -----
    If the href element is not a valid url, then the href element is
    appended to the given url.

    """
    href = []
    for _a in a:
        # if no href attribute is given in the tag, the initial url is returned
        _href = _a.get("href", url)
        if "https" in _href:
            href.append(_href)
        else:
            href.append(url + _href)
    return href


class Parser(Webscraper):

    def __init__(
        self,
        parser: str,
        verbose: bool = False
    ) -> None:
        super().__init__(parser, verbose=verbose)

    def _scrape(
        self,
        tag: str,
        element: DATA_OBJECT,
        fun: Callable,
        *args,
    ) -> Dict[str, list]:
        """Get all html elements defined by `tag`.

        Parameters
        ----------
        tag : str
            The tag which should be searched in the html page.
        element : DATA_OBJECT
            The element to be parsed, this can be:

            * None: If None, then the self._data attribute is parsed.
            * Beautifulsoup: Parse the given Beautifulsoup element.
            * List[Beautifulsoup]: Parse the given Beautifulsoup elements.

        fun : Callable
            The function which loads the element to a specific data type.
        args : tuple
            Additional arguments passed to ``fun``.

        Returns
        -------
        Dict[str, list]
            Return a dictionary containing the url as key and the
            corresponding elements as list.

        Notes
        -----
        If no `element` is given to be searched, then the url(s) is(are)
        searched for only ``tag`` elements.

        Raises
        ------
        AssertionError
            If element is not of type list or Beautifulsoup.

        """
        data = {}
        if not element:
            self.parse(name=tag)
            element = self._data
        if isinstance(element, list):
            if len(element) == 1:
                html_ele = element[0](tag)
                data[self._url] = fun(html_ele, *args)
            else:
                for idx, ele in enumerate(element):
                    # catch if there is a bs4 Tag or ResultSet returned
                    html_ele = ele(tag) if isinstance(
                        ele, Tag) else ele[0](tag)
                    data[self._url[idx]] = fun(html_ele, *args)
        elif isinstance(element, BeautifulSoup):
            html_ele = element(tag)
            data[self._url] = fun(html_ele, *args)
        else:
            raise AssertionError(
                f"Parameter element is not of type {list} nor of type {BeautifulSoup}, it is of type {type(element)}!")
        return data

    def href(
        self,
        element: DATA_OBJECT
    ) -> Dict[str, List[str]]:
        """Get all href of <a></a> elements of the given url(s).

        See the documentation for ``self._scrape()`` for a documentation oif
        additional parameters.
        """
        tag = "a"
        data = self._scrape(tag, element, _get_href, self._url)
        return data

    def table(
        self,
        element: DATA_OBJECT,
    ) -> Dict[str, List[pd.DataFrame]]:
        """Get all <table></table> elements of the given url(s) as
        DataFrame(s).

        See the documentation for ``self._scrape()`` for a documentation oif
        additional parameters.

        """
        tag = "table"
        data = self._scrape(tag, element, _get_tables)
        return data
