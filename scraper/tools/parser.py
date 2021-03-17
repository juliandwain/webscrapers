# -*- coding: utf-8 -*-

__doc__ = """
"""

from typing import Dict, List

import pandas as pd
from bs4 import BeautifulSoup

from ..webscraper import DATA_OBJECT, Webscraper

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

    def table(
        self,
        element: DATA_OBJECT,
    ) -> Dict[str, List[pd.DataFrame]]:
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
        Dict[str, List[pd.DataFrame]]
            Return a dictionary containing the url as key and the
            corresponding table elements as list.

        Notes
        -----
        If no `element` is given to be searched, then the url(s) is(are)
        searched for only table elements.

        Raises
        ------
        AssertionError
            If element is not of type list or Beautifulsoup.

        """
        tag = "table"
        dfs = {}
        if not element:
            # parse the document only for tables
            self.parse(name=tag)
            element = self._data
        if isinstance(element, list):
            if len(element) == 1:
                tables = element[0](tag)  # find all table elements
                dfs[self._url] = _get_tables(
                    tables, element[0].original_encoding)
            else:
                for idx, ele in enumerate(element):
                    tables = ele(tag)  # find all table elements
                    dfs[self._url[idx]] = _get_tables(
                        tables, ele.original_encoding)
        elif isinstance(element, BeautifulSoup):
            tables = element(tag)  # find all table elements
            dfs[self._url] = _get_tables(tables, element.original_encoding)
        else:
            raise AssertionError(
                f"Parameter element is not of type {list} nor of type {BeautifulSoup}, it is of type {type(element)}!")
        return dfs
