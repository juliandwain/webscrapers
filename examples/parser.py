# -*- coding: utf-8 -*-

__doc__ = """
This is an example on how to create a parser, which parses
``Beautifulsoup`` objects for given elements, i.e., tables, pictures, etc.
"""

import scraper.webscraper as ws


class Parser(ws.Webscraper):

    def __init__(self, parser: str, verbose: bool = False) -> None:
        super().__init__(parser, verbose=verbose)

    def tables(self):
        """Parse the object for <table><\table> elements.
        """
