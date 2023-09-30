import settings


def get_full_link(hero_dotabuff_name, date_filter):
    return settings.DOTABUFF_ALL_HEROES_LINK + hero_dotabuff_name + \
           settings.DOTABUFF_COUNTERS_LINK_SUFFIX + f'?date={date_filter}'


def future_with_hero_generator(hero_list, link, session, timeout=50):
    for hero in hero_list:
        future_with_hero = session.get(settings.DOTABUFF_ALL_HEROES_LINK + hero.dotabuff_name,
                                       headers=settings.HEADERS,
                                       timeout=timeout)
        future_with_hero.hero = hero
        yield future_with_hero


def future_generator_for_hero_winrate_matrix(hero_list, filter_param, session, timeout=50):
    for hero in hero_list:
        future_with_hero = session.get(get_full_link(hero.dotabuff_name, filter_param),
                                       headers=settings.HEADERS,
                                       timeout=timeout)
        future_with_hero.hero = hero
        yield future_with_hero


def future_generator_for_ally(hero_soup, session, timeout=50):
    base_link = r"https://dota2.fandom.com"

    for hero_div in hero_soup.find_all(class_="heroentry"):
        hero_div = hero_div.find("a")
        hero_name = hero_div["title"]

        r_hero = session.get(base_link + hero_div["href"] + "/Counters", headers=settings.HEADERS)
        r_hero.hero_name = hero_name
        yield r_hero
