# -*- coding: utf-8 -*-

__doc__ = """
This is an example on how to extend the ``Webscraper`` class to
save pictures to files.
"""

import os
import pathlib
from typing import Union

import scraper.webscraper as ws


class PhotoSaver(ws.Webscraper):
    def __init__(self, parser: str, verbose: bool = False) -> None:
        super().__init__(parser, verbose=verbose)

    def save(self, path: Union[str, os.PathLike]) -> None:
        """Save a downloaded image to a file.

        Parameters
        ----------
        path : Union[str, PathLike]
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
        if isinstance(path, str):
            _path = pathlib.Path(path)
        else:
            _path = path
        if isinstance(self.res, list):
            for i, res in enumerate(self.res):
                __path = _path / f"picture-{i}.png"
                with __path.open(mode="wb", encoding=res.encoding) as pic:
                    for chunk in res.iter_content(chunk_size=128):
                        pic.write(chunk)
        else:
            with _path.open(mode="wb", encoding=self.res.encoding) as pic:
                for chunk in self.res.iter_content(chunk_size=128):
                    pic.write(chunk)


if __name__ == "__main__":
    parser = "html.parser"
    url = "https://api.corona-zahlen.org/map/districts"
    path = os.path.join(os.path.abspath(""), "examples/figs/districts.png")
    print(path)

    photo_saver = PhotoSaver(parser, verbose=True)
    photo_saver.load(url)
    photo_saver.save(path)
