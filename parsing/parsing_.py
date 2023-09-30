import contextlib
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import requests
import shutil
import logging

from pathlib import Path
from bs4 import BeautifulSoup

from model import Hero
# from db.read_api import get_basic_hero_list
# from utils.general import get_web_server_resources_dir, get_static_web_server_dir, \
#     ALLIES_FROM_DOTA_WIKI_FILE_PATH, get_resources_dir

import settings
from parsing.generators import future_with_hero_generator, future_generator_for_hero_winrate_matrix, \
    future_generator_for_ally
from parsing.support_func import get_dotabuff_soup
from utils import get_hero_images_dir, get_resources_dir, get_allies_file_path

from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

IMAGE_DIR = get_hero_images_dir()
ADDITIONAL_ROLES_DIR = get_resources_dir() / Path('additional_roles')

logger = logging.getLogger(__name__)


def get_filters():
    """ getting all filters based on settings.BASE_FILTER_KEYS_FROM_DOTABUFF and last accessable patch """

    soup = get_dotabuff_soup(settings.DOTABUFF_ALL_HEROES_WINRATE_LINK)
    all_filters = []
    last_patch_filter = soup.find_all('option', attrs={'value': lambda val: val.startswith("patch")})
    last_patch_filter = last_patch_filter[0]['value']
    all_filters.append(last_patch_filter)

    return all_filters + settings.BASE_FILTER_KEYS_FROM_DOTABUFF


def get_list_of_hero_only_names():
    """ Create list of Hero objects but only name and dotabuff_name included. """

    hero_list = []

    soup = get_dotabuff_soup(settings.DOTABUFF_ALL_HEROES_LINK)

    for h in soup.find_all(class_='hero'):
        new_hero = Hero()

        new_hero.name = h.find('div').text
        new_hero.dotabuff_name = h.parent['href'].split(r'/')[-1]

        hero_list.append(new_hero)

    return hero_list


def get_general_winrate_by_hero_list(hero_list):
    """ add general_winrate attribute for copies of hero_list based on filters. """

    logger.debug('Add general winrates to heroes based on filters...')

    soup = get_dotabuff_soup(settings.DOTABUFF_ALL_HEROES_WINRATE_LINK)

    # {filter: list(heroes)}
    filter_heroes_dict = {}
    filters = get_filters()

    for filter_ in filters:
        soup = get_dotabuff_soup(settings.DOTABUFF_ALL_HEROES_WINRATE_LINK + f"?date={filter_}")
        new_hero_list = [hero.copy() for hero in hero_list]

        for hero in new_hero_list:
            cell = soup.find("td", attrs={'class': 'cell-icon', 'data-value': f"{hero.name}"})
            hero.general_winrate = float(cell.parent.find_all('td')[2]['data-value'])
        filter_heroes_dict[filter_] = new_hero_list

    return filter_heroes_dict


def download_default_images_for_hero_list(hero_list):
    """ adding default images into root_dir/resoursec/default_hero_images dir. """

    logger.debug('Downloading default images...')

    soup = get_dotabuff_soup(settings.DOTABUFF_ALL_HEROES_WINRATE_LINK)

    for hero in hero_list:
        cell = soup.find("td", attrs={'class': 'cell-icon', 'data-value': f"{hero.name}"})
        image_soup = cell.find('img', class_='image-hero')['src']
        r_image = requests.get(settings.DOTABUFF_LINK_PREFIX + image_soup, stream=True, headers=settings.HEADERS)

        with open(IMAGE_DIR / f"{hero.dotabuff_name}.jpg", 'wb') as f:
            shutil.copyfileobj(r_image.raw, f)


def assign_roles_set_for_hero_list(hero_list):
    """ Add roles to each hero from dotabuff. """

    for hero in hero_list:
        hero.roles_set = set()

    with FuturesSession(executor=ProcessPoolExecutor(max_workers=settings.PARSING_NUMBER_OF_WORKERS)) as session:
        futures = future_with_hero_generator(hero_list, settings.DOTABUFF_ALL_HEROES_LINK + hero.dotabuff_name,
                                             session, timeout=settings.PARSING_TIMEOUT)
        for future in as_completed(futures):
            response = future.result()
            soup = BeautifulSoup(response.text, 'html.parser')

            future.hero.roles_set = set(soup.find('h1').find('small').text.split(', '))

    hero_dict = {v.dotabuff_name: v for v in hero_list}
    for file in ADDITIONAL_ROLES_DIR.iterdir():
        if file.is_file():
            with open(file, 'r') as f:
                for line in f:
                    if line.strip() in hero_dict.keys():
                        hero_dict[line.strip()].roles_set.add(f.name.split("\\")[-1])


def get_dict_for_hero_winrate_matrix(hero_list):
    """ Gets winrate matchups from dotabuff and update winrate_dict for Hero objects. """

    result_dict = {}  # {filter: hero_list}
    hero_dict = {hero.dotabuff_name: hero for hero in hero_list}

    for filter_ in get_filters():
        new_hero_list = [hero.copy() for hero in hero_list]

        with FuturesSession(executor=ProcessPoolExecutor(max_workers=settings.PARSING_NUMBER_OF_WORKERS)) as session:
            futures = future_generator_for_hero_winrate_matrix(new_hero_list, filter_,
                                                               session, timeout=settings.PARSING_TIMEOUT)
            for future in as_completed(futures):
                response = future.result()
                soup = BeautifulSoup(response.text, 'html.parser')
                soup_conters_list = soup.find('header', string='Matchups').find_next(
                    'table').find_all('tr', attrs={'data-link-to': True})

                future.hero.winrate_dict = {}
                for soup_enemy in soup_conters_list:
                    enemy_name = soup_enemy['data-link-to'].split('/')[-1]
                    enemy_winrate_against = soup_enemy.find_all('td')[2]['data-value']
                    enemy_winrate_against = -float(enemy_winrate_against)
                    # winrate_dict: {Hero: winrate}
                    future.hero.winrate_dict[hero_dict[enemy_name]] = enemy_winrate_against

        result_dict[filter_] = new_hero_list

    return result_dict


def parse_allies_from_dota_wiki():
    """ Find best allies for heroes form dota wiki.

        Save allies to specific file (ALLIES_FROM_DOTA_WIKI_FILE_PATH).
    """

    base_link = r"https://dota2.fandom.com"
    link_to_hero_page = r"https://dota2.fandom.com/wiki/Dota_2_Wiki"
    r = requests.get(link_to_hero_page, headers=settings.HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')

    hero_list = get_list_of_hero_only_names()

    hero_dict = {hero.name.lower(): hero.dotabuff_name for hero in hero_list}
    with open(get_allies_file_path(), "w") as file:
        with FuturesSession(executor=ProcessPoolExecutor(max_workers=settings.PARSING_NUMBER_OF_WORKERS)) as session:
            futures = future_generator_for_ally(soup,
                                                session, timeout=settings.PARSING_TIMEOUT)
            for future in as_completed(futures):
                response = future.result()
                soup_hero = BeautifulSoup(response.text, 'html.parser')
                soup_hero = soup_hero.find(id="Works_well_with...").parent
                all_allies_div = soup_hero.find_all_next("div")

                allies_for_this_hero = []
                for potential_ally in all_allies_div:
                    ally = potential_ally.find("b")
                    if ally:
                        allies_for_this_hero.append(ally.find("a")["title"])

                file.write(
                    f"{hero_dict[future.hero_name.lower()]}: {', '.join([hero_dict[hero.lower()] for hero in allies_for_this_hero])}")
                file.write("\n")


if __name__ == '__main__':
    parse_allies_from_dota_wiki()
    # hero_list = get_list_of_hero_only_names()
    # filter_hero_list_dict = get_dict_for_hero_winrate_matrix(hero_list)
    # download_default_images_for_hero_list(hero_list)
