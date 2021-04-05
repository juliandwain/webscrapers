# XSCRAPERS

The [XSCRAPERS](https://github.com/juliandwain/webscrapers) package provides an OOP interface to some simple webscraping techniques.

A base use case can be to load some pages to [Beautifulsoup Elements](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
This package allows to load the URLs concurrently using multiple threads, which allows to safe an enormous amount of time.

```python
import xscrapers.webscraper as ws

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

## Downloading the Firefox Geckodriver

### Linux

See [this link](https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu) for a good explanation.
In short, the steps are:

1. Download the geckodriver from the [mozilla GitHub release page](https://github.com/mozilla/geckodriver/releases), note to change the `X` for the version you want to download

    ```properties
    wget https://github.com/mozilla/geckodriver/releases/download/vX.XX.X/geckodriver-vX.XX.X-linux64.tar.gz
    ```

2. Extract the file with

    ```properties
    tar -xvzf geckodriver*
    ```

3. Make it executable

    ```properties
    chmod +x geckodriver
    ```

4. In the last step, the driver can be added to the `PATH` environment variable, moved to the `usr/local/bin` folder, or can be given as full path to the `Webdriver` class as `exe_path` argument

    ```properties
    export PATH=$PATH:/path-to-extracted-file/
    sudo mv geckodriver /usr/local/bin/
    ```
