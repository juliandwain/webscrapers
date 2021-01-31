# -*- coding: utf-8 -*-

__doc__ = """This is another test module.
"""

import time

import scraper.webscraper as ws

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

if __name__ == "__main__":

    webscraper = ws.Webscraper(PARSER, verbose=True)

    # start = time.time()
    # response = webscraper.load(URL)
    # obj = webscraper.parse(response)
    # end = time.time()
    # dur = end - start
    # print(f"Response of 1 object took {dur:.2f}s.")
#
    # start = time.time()
    # reponses = []
    # for url in tqdm(LIST_OF_URLS):
    #     reponses.append(webscraper.load(url))
    # end = time.time()
    # dur = end - start
    # print(
    #     f"Response of {len(LIST_OF_URLS)} objects took {dur:.2f}s in serial.")

    start = time.time()
    webscraper.load(LIST_OF_URLS)
    end = time.time()
    dur = end - start
    print(
        f"Response of {len(LIST_OF_URLS)} objects took {dur:.2f}s in parallel.")
    webscraper.parse()
    print(webscraper)
