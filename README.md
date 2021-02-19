# XSCRAPERS

The [XSCRAPERS](https://github.com/juliandwain/webscrapers) package provides an OOP interface to some simple webscraping techniques.

A base use case can be to load some pages to [Beautifulsoup Elements](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
This package allows to load the URLs concurrently using multiple threads, which allows to safe an enormous amount of time.

```python
import scraper.webscraper as ws

URLS = [
    "https://www.google.com/",
    "https://www.amazon.com/",
    "https://www.youtube.com/",
]
PARSER = "html.parser"
web_scraper = ws.Webscraper(PARSER, verbose=True)
web_scraper.load(URLS)
web_scraper.parse()

```

Note that herein, the data scraped is stored in the `data` attribute of the webscraper.
The URLs parsed are stored in the `url` attribute.
