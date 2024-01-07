# -*- coding: utf-8 *-*

from setuptools import setup

setup(
    name="mm_scraper",
    version="0.0.1",
    author="Michael Füllbier",
    author_email="mm_scraper@e-milia.de",
    description="Scraper für Media Markt Fundgrupe",
    license="MIT",
    keywords="Media Markt Fundgrupe",
    install_requires=["requests", "python-telegram-bot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["mm_scraper=main:main"]},
)
