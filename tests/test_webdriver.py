# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

import xscrapers.webdriver as wd


class TestWebDriver(unittest.TestCase):

    def setUp(self) -> None:
        self.url = "https://www.investing.com/"
        self.exe_path = Path("./drivers/debian/geckodriver")
        self.webdriver = wd.Webdriver(self.url, self.exe_path)
        self.title = "Investing.com - Stock Market Quotes & Financial News"

    def tearDown(self) -> None:
        return super().tearDown()

    def test_load_page(self):
        with self.webdriver:
            assert self.title == self.webdriver.engine.title

    def test_parse_page(self):
        by = "css_selector"
        val = "#navMenu > ul > li:nth-child(1) > a"
        with self.webdriver:
            html = self.webdriver.parse(by)
            assert isinstance(html, list)
            link = self.webdriver.parse(
                by,
                element=html[0],
                val=val,
            )
            assert isinstance(link, list)
            self.webdriver.click_hyperlink(link[0])
            assert self.title == self.webdriver.engine.title

    def test_driver_init(self):
        pass


if __name__ == '__main__':
    unittest.main()
