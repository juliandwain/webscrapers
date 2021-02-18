# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="webscrapers",
    version="0.0.1",
    author="Julian Dwain Stang",
    author_email="julian.stang@web.de",
    description=("A simple webscraping framework."),
    license="MIT",
    url="https://github.com/juliandwain/webscrapers",
    packages=find_packages(),
    long_description=read("README.md"),
)
