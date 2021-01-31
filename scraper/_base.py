# -*- coding: utf-8 -*-

import abc

__doc__ = """The base class.
"""


class Scraper(abc.ABC):
    """The base scraper class.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def load(self):
        """Abstract method for loading url content.
        """

    @abc.abstractmethod
    def parse(self):
        """Abstract method for parsing url content.
        """
