# -*- coding: utf-8 -*-

__doc__ = """This module servers as a test file.
"""

import scraper.webdriver as wd
from pathlib import Path

EXE_PATH = Path("./drivers/debian/geckodriver")

URL = "https://www.investing.com/"

BY = "css_selector"
IDX = None

driver = wd.Webdriver(URL, EXE_PATH, headless=True)

with driver:
    # get the full html
    html = driver.parse(BY)[0]
    # get the hyperlink to the markets
    markets_link = driver.parse(
        BY,
        element=html,
        val="#navMenu > ul > li:nth-child(1) > a"
    )[0]
    # click the hyperlink
    driver.click_hyperlink(markets_link)
    print(driver.engine.title)
