# -*- coding: utf-8 -*-

from scraper import Webdriver

URL = "https://www.google.de/"

driver = Webdriver(URL, headless=False)

with driver:
    print(driver.engine)
