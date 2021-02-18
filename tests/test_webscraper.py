# -*- coding: utf-8 -*-

import time
import unittest

import webscraper as ws


class TestWebScraper(unittest.TestCase):

    def setUp(self):
        self.url = "http://httpbin.org/"
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

    def tearDown(self):
        pass

    def test_single_url(self):
        start = time.time()
        self.webscraper.load(self.urls)
        end = time.time()
        dur = end - start
        print(
            f"Response of {len(self.urls)} objects took {dur:.2f}s in parallel.")


if __name__ == '__main__':
    unittest.main()
