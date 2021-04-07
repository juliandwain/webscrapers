# -*- coding: utf-8 -*-

__doc__ = """
This is an example on how to extend the ``Webscraper`` class to
save pictures to files.
"""

import os
import pathlib
from typing import Union

import xscrapers.webscraper as ws

PATH_LIKE = Union[str, os.PathLike]


class PhotoSaver(ws.Webscraper):
    def __init__(self, parser: str, verbose: bool = False) -> None:
        self._chunk_size = 256
        super().__init__(parser, verbose=verbose)

    def save(self, path: PATH_LIKE) -> None:
        """Save a downloaded image to a file.

        Parameters
        ----------
        path : PATH_LIKE
            The path in which the file should be saved.

        Notes
        -----
        The behaviour of this function changes depending on the amount of
        urls loaded. If multiple urls are given, ``path`` points only to
        the directory where the files are saved. If only one file is saved,
        then the filename must be specified as well.

        References
        ----------
        [1] https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests

        """
        # TODO: error handling for path
        if isinstance(path, str):
            _path = pathlib.Path(path)
        else:
            _path = path
        if isinstance(self.res, list):
            if _path.parts[-2] == ".":
                raise AssertionError(
                    f"When saving multiple photos at once, there can only be a folder given, not a single filename!")
            for i, res in enumerate(self.res):
                content_type = res.headers["Content-Type"].split("/")[-1]
                __path = _path / f"picture-{i}.{content_type}"
                with __path.open(mode="wb", encoding=res.encoding) as pic:
                    for chunk in res.iter_content(chunk_size=self._chunk_size):
                        pic.write(chunk)
        else:
            with _path.open(mode="wb", encoding=self.res.encoding) as pic:
                for chunk in self.res.iter_content(chunk_size=self._chunk_size):
                    pic.write(chunk)


if __name__ == "__main__":
    parser = "html.parser"
    url = "http://httpbin.org/image/png"
    urls = [
        r"http://httpbin.org/image/jpeg",
        r"http://httpbin.org/image/png",
        r"http://httpbin.org/image/svg",
        r"http://httpbin.org/image/webp",
    ]
    params = {
        "stream": True,
    }
    path = os.path.join(os.path.abspath(""), "examples/figs/")
    filename = "image.png"
    print(path)

    photo_saver = PhotoSaver(parser, verbose=True)
    photo_saver.get(url, params)
    photo_saver.save(os.path.join(path, filename))

    photo_saver.get(urls, params)
    photo_saver.save(path)
