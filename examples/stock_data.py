# -*- coding: utf-8 -*-

__doc__ = """This is an example on how to download
the DAX and DowJones data as html table to pandas DataFrames, and 
also modify the DataFrames to extract relevant information.

In general, there are 2 methods to get the data.

1 Parse the Full HTML Page
==========================

Parsing the full html page is very inefficient considering memory allocation,
but has as advantage that after "having" the full html element stored,
one can locate the html element in which the desired table is stored.

2 Parse only <table></table> elements on the webpage
====================================================

Parsing only the html table elements is much more efficient considering memory
and speed, but this requires the user to manually filter for the desired table.

"""

import xscrapers.tools as tools

# define the parser object
parser = tools.Parser(parser="html.parser", verbose=True)
# define the url
urls = [
    "https://www.finanzen.net/aktien/dax-realtimekurse",
    "https://www.finanzen.net/aktien/dow_jones-realtimekurse"
]
# load the urls
parser.get(urls)

# method 1
# get only the html element where the relevant table is located
parser.parse()  # parse the full html element
# search for the given element by calling the data attribute
# TODO: This is unintuitive, only one way of calling this
html_ele = []
for html in parser.data:
    html_ele.append(
        html.find("div", attrs={"class": "table-responsive relative"}))
# pass the html elements to the table method to extract the table
dfs_1 = parser.table(element=html_ele)
dax_data_1 = dfs_1[urls[0]][0]
dow_data_1 = dfs_1[urls[1]][0]
print(dax_data_1)
print(dow_data_1)

# method 2
# set the data attribute to None (only for this example)
parser.data = None
# get all table elements as dataframes
dfs_2 = parser.table(element=None)
# save the data as dataframes
dax_data_2 = dfs_2[urls[0]][5]
dow_data_2 = dfs_2[urls[1]][5]
print(dax_data_2)
print(dow_data_2)
