# -*- coding: utf-8 -*-

import gzip
import time
import unittest
from pathlib import Path

import xscrapers.webscraper as ws
from bs4 import BeautifulSoup


class TestWebScraper(unittest.TestCase):

    def setUp(self):
        self.url = r"http://httpbin.org/"
        self.urls = [
            r"http://www.youtube.com",
            r"http://www.facebook.com",
            r"http://www.baidu.com",
            r"http://www.yahoo.com",
            r"http://www.amazon.com",
            r"http://www.wikipedia.org",
            r"http://www.qq.com",
            r"http://www.google.co.in",
            r"http://www.twitter.com",
            r"http://www.live.com",
            r"http://www.taobao.com",
            r"http://www.bing.com",
            r"http://www.instagram.com",
            r"http://www.weibo.com",
            r"http://www.sina.com.cn",
            r"http://www.linkedin.com",
            r"http://www.yahoo.co.jp",
            r"http://www.msn.com",
            r"http://www.vk.com",
            r"http://www.google.de",
            r"http://www.yandex.ru",
            r"http://www.hao123.com",
            r"http://www.google.co.uk",
            r"http://www.reddit.com",
        ]
        self.parser = "html.parser"
        self.webscraper = ws.Webscraper(self.parser, verbose=True)

        self.test_path = Path("tests/etc")
        self.test_path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        pass

    def test_multiple_url(self):
        start = time.time()
        self.webscraper.get(self.urls)
        end = time.time()
        dur = end - start
        print(
            f"Response of {len(self.urls)} objects took {dur:.2f}s in parallel.")
        assert self.webscraper._http_request["GET"]
        assert isinstance(self.webscraper.url, list)

    def test_single_url(self):
        self.webscraper.get(self.url)
        dur = self.webscraper.res.elapsed.total_seconds()
        print(f"Response of single object took {dur:.2f}s.")
        assert self.webscraper._http_request["GET"]
        assert isinstance(self.webscraper.url, str)

    def test_multiple_parse(self):
        self.webscraper.get(self.urls)
        self.webscraper.parse()
        assert isinstance(self.webscraper.data, list)

    def test_single_parse(self):
        self.webscraper.get(self.url)
        self.webscraper.parse()
        assert isinstance(self.webscraper.data, BeautifulSoup)

    def test_http_methods(self):
        methods = (
            "DELETE",
            "GET",
            "PATCH",
            "POST",
            "PUT",
        )
        functions = (
            self.webscraper.delete,
            self.webscraper.get,
            self.webscraper.patch,
            self.webscraper.post,
            self.webscraper.put,
        )
        for function, method in zip(functions, methods):
            url = self.url + method.lower()
            function(url)
            assert self.webscraper._http_request[method]

    def test_auth(self):
        pass

    def test_status_codes(self):
        status_codes = list(range(100, 600, 100))
        urls = [self.url +
                f"/status/{status_code}" for status_code in status_codes]
        self.webscraper.get(urls)

    def test_request_inspection(self):
        inspections = (
            "headers",
            "ip",
            "user-agent",
        )
        for inspection in inspections:
            url = self.url + inspection
            self.webscraper.get(url)

    def test_response_inspection(self):
        pass

    def test_response_formats(self):
        plain_data = {
            "deny": ("text/plain", "txt"),
            "encoding/utf8": ("text/html; charset=utf-8", "html"),
            "html": ("text/html; charset=utf-8", "html"),
            "json": ("application/json", "json"),
            "robots.txt": ("text/plain", "txt"),
            "xml": ("application/xml", "xml"),
        }
        encoded_data = {
            "brotli": ("br", None),
            "deflate": ("deflate", None),
            "gzip": ("gzip", gzip.open),
        }
        for i, (format, (code, fun)) in enumerate(encoded_data.items()):
            url = self.url + format
            self.webscraper.get(url)
            encoding = self.webscraper.res.headers["Content-Encoding"]
            assert encoding == code

        for i, (format, (code, file_type)) in enumerate(plain_data.items()):
            url = self.url + format
            self.webscraper.get(url)
            content_type = self.webscraper.res.headers["Content-Type"]
            encoding = self.webscraper.res.encoding
            assert content_type == code
            file = self.test_path / f"test-{i}.{file_type}"
            with file.open(mode="w", encoding=encoding) as f:
                f.write(self.webscraper.res.text)

    def test_dynamic_data(self):
        pass

    def test_cookies(self):
        pass

    def test_images(self):
        pass

    def test_redirects(self):
        pass

    def test_anything(self):
        pass


if __name__ == '__main__':
    unittest.main()
