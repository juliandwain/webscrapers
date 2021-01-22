# -*- coding: utf-8 -*-

from scraper import Webdriver

URL = "https://www.google.de/"

BY = "css_selector"
IDX = None

driver = Webdriver(URL, headless=False)

with driver:
    print(driver.engine)
    ele = driver.find_object(BY, IDX)
