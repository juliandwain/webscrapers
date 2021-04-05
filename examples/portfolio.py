# -*- coding: utf-8 -*-

__doc__ = """This is an example of how to extract data for a given portfolio.

Herein, the link to the stokcs, bonds, ETFs, etc. is given the scraper which
thereafter scrapes the webpage for the needed information.

"""

from typing import TypeVar
import xscrapers.tools as tools

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class Portfolio(dict):
    def __init__(self, *args):
        dict.__init__(self, args)
        self._data = {}

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, val) -> None:
        self._data = val

    def __getitem__(self, k: _KT) -> _VT:
        return super().__getitem__(k)

    def __setitem__(self, k: _KT, v: _VT) -> None:
        for key, value in v.items():
            self._data[key] = value
        return super().__setitem__(k, self._data)

    def __repr__(self) -> str:
        msg = f"Portfolio Information\n"
        msg += "=" * (len(msg)-1) + "\n\n"
        for company, data in self.items():
            msg += company + "\n"
            msg += "-" * (len(company)-1) + "\n"
            msg += f"WKN: {data['WKN']}\nISIN: {data['ISIN']}\n"
            msg += f"Stock Data: {data['Stock Data']}\n"
            msg += f"Source: {data['Source']}\n\n"
        return msg


parser = tools.Parser(parser="html.parser", verbose=True)

urls = [
    "https://www.finanzen.net/aktien/allianz-aktie",
    "https://www.finanzen.net/aktien/daimler-aktie",
    "https://www.finanzen.net/aktien/deutsche_telekom-aktie",
    "https://www.finanzen.net/aktien/tui-aktie",
]
# load the urls
parser.get(urls)

# create an empty dictionry in which the data is stored
portfolio = Portfolio()

# get all table elements
dfs = parser.table(element=None)
# set the data attribute to None to parse the whole html
parser.data = None
# parse the whole html page as more than one element are needed
parser.parse()
for url, html in zip(urls, parser.data):
    # save the name, WKN, and ISIN
    h1 = html.find("h1", attrs={"class": "font-resize"})
    name, wkn_isin = h1.text.split("\xa0")
    wkn = wkn_isin.split(" ")[1]
    isin = wkn_isin.split(" ")[-1]
    portfolio[name] = {
        "WKN": wkn,
        "ISIN": isin
    }
    # obtain all relevant tables for each url
    stock_data = dfs[url][7]
    key_factors_1 = dfs[url][14]
    key_factors_2 = dfs[url][15]
    portfolio[name] = {
        "Stock Data": stock_data,
        "Key Factors 1": key_factors_1,
        "Key Factors 2": key_factors_2,
    }
    info_box = html.find("div", attrs={"class": "box infoBox"})
    portfolio[name] = {"Source": url}
print(portfolio)
