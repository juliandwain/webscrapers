# -*- coding: utf-8 -*-

__doc__ = """This file servers as a test file.
"""

from scraper import Webdriver

URL = "https://www.investing.com/"

BY = "css_selector"
IDX = None

driver = Webdriver(URL, headless=False)

with driver:
    # get the full html
    html = driver.find_object(BY)
    # get the hyperlink to the markets
    markets_link = driver.find_object(
        BY,
        element=html,
        val="#navMenu > ul > li:nth-child(1) > a"
    )
    # click the hyperlink
    driver.click_hyperlink(markets_link)
    print(driver.engine.title)
