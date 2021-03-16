# -*- coding: utf-8 -*-

__doc__ = """
"""

from typing import Dict, List

import pandas as pd
from ..webscraper import Webscraper, DATA_OBJECT
from bs4 import BeautifulSoup, SoupStrainer

__all__ = [
    "Parser",
]


def _get_tables(
    tables: list,
    encoding: str
) -> List[pd.DataFrame]:
    """Get <table></table> elements as dataframe.

    Parameters
    ----------
    tables : list
        The list of html tables.
    encoding : str
        The original encoding of the webpage.

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
            encoding=encoding,
        )[0]
        df.append(_df)
    return df


class Parser(Webscraper):

    def __init__(
        self,
        parser: str,
        verbose: bool = False
    ) -> None:
        super().__init__(parser, verbose=verbose)

    def tables(
        self,
        element: DATA_OBJECT,
    ) -> Dict[str, list]:
        """Get all <table></table> elements of the given url(s) as
        DataFrame(s).

        Parameters
        ----------
        element : DATA_OBJECT
            The element to be parsed, this can be:

            * None: If None, then the self._data attribute is parsed.
            * Beautifulsoup: Parse the given Beautifulsoup element.
            * List[Beautifulsoup]: Parse the given Beautifulsoup elements.

        Returns
        -------
        Dict[str, list]
            Return a dictionary containing the url as key and the
            corresponding table elements as list.

        Raises
        ------
        AssertionError
            If element is not of type list or Beautifulsoup.

        """
        tag = SoupStrainer("table")
        dfs = {}
        if not element:
            element = self._data
        if isinstance(element, list):
            for idx, ele in enumerate(element):
                tables = ele(tag)
                dfs[self._url[idx]] = _get_tables(
                    tables, ele.original_encoding)
        elif isinstance(element, BeautifulSoup):
            tables = element(tag)
            dfs[self._url] = _get_tables(tables, element.original_encoding)
        else:
            raise AssertionError(
                f"Parameter element is not of type {list} nor of type {BeautifulSoup}, it is of type {type(element)}!")
        return dfs
