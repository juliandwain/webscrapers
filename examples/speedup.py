# -*- coding: utf-8 -*-

__doc__ = """
This is a simple example showing the possible speedup obtained by
making requests in parallel threads instead of serializing them.
"""

import time

import xscrapers.webscraper as ws
from tqdm import tqdm

URL = "http://httpbin.org/"
LIST_OF_URLS = [
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
PARSER = "html.parser"

webscraper = ws.Webscraper(PARSER, verbose=True)

start = time.time()
response = webscraper.get(URL)
webscraper.parse()
end = time.time()
dur = end - start
print(f"Response of 1 object took {dur:.2f}s.")

start = time.time()
for url in tqdm(LIST_OF_URLS):
    webscraper.get(url)
end = time.time()
dur = end - start
print(
    f"Response of {len(LIST_OF_URLS)} objects took {dur:.2f}s in serial.")

start = time.time()
webscraper.get(LIST_OF_URLS)
end = time.time()
dur = end - start
print(
    f"Response of {len(LIST_OF_URLS)} objects took {dur:.2f}s in parallel.")
