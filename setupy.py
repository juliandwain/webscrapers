# -*- coding: utf-8 -*-

import os

import setuptools

from scraper import __version__


def read(fname: str):
    with open(os.path.join(os.path.dirname(__file__), fname), mode="r", encoding="utf-8") as file:
        if fname == "README.md":
            data = file.read()
        else:
            data = file.read().splitlines()
    print(type(data))
    return data


setuptools.setup(
    name="webscrapers",
    version=__version__,
    author="Julian Dwain Stang",
    author_email="julian.stang@web.de",
    description=("A simple webscraping framework."),
    license="MIT",
    url="https://github.com/juliandwain/webscrapers",
    packages=setuptools.find_packages(),
    long_description=read("README.md"),
    install_requires=read("requirements.txt"),
    python_requires=">=3.8",
)
