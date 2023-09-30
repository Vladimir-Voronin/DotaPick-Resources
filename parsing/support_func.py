import requests
from bs4 import BeautifulSoup

import settings


def get_dotabuff_soup(link):
    """ return a BeautifulSoup object for any dotabuff link. """

    r = requests.get(link, headers=settings.HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_dotabuff_soup_session(link, session):
    """ return a BeautifulSoup object for any dotabuff link.

        Session speedup this function compare to get_dotabuff_soup().
    """

    r = session.get(link, headers=settings.HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup
