# -*- coding: utf-8 -*-

__doc__ = """This is another test module.
"""

import time

from tqdm import tqdm

import scraper.webscraper as ws

URL = "http://httpbin.org/"
LIST_OF_URLS = [
    "http://www.youtube.com",
    "http://www.facebook.com",
    "http://www.baidu.com",
    "http://www.yahoo.com",
    "http://www.amazon.com",
    "http://www.wikipedia.org",
    "http://www.qq.com",
    "http://www.google.co.in",
    "http://www.twitter.com",
    "http://www.live.com",
    "http://www.taobao.com",
    "http://www.bing.com",
    "http://www.instagram.com",
    "http://www.weibo.com",
    "http://www.sina.com.cn",
    "http://www.linkedin.com",
    "http://www.yahoo.co.jp",
    "http://www.msn.com",
    "http://www.vk.com",
    "http://www.google.de",
    "http://www.yandex.ru",
    "http://www.hao123.com",
    "http://www.google.co.uk",
    "http://www.reddit.com",
]
PARSER = "HTML.PARSER"

webscraper = ws.Webscraper(PARSER)

# start = time.time()
# response = webscraper.load_url(URL)
# end = time.time()
# dur = end - start
# print(f"Response of 1 object took {dur:.2f}s.")
#
# start = time.time()
# reponses = []
# for url in tqdm(LIST_OF_URLS):
#     reponses.append(webscraper.load_url(url))
# end = time.time()
# dur = end - start
# print(f"Response of {len(LIST_OF_URLS)} objects took {dur:.2f}s in serial.")

start = time.time()
responses_ = webscraper.load_urls(LIST_OF_URLS)
end = time.time()
dur = end - start
print(f"Response of {len(LIST_OF_URLS)} objects took {dur:.2f}s in parallel.")
