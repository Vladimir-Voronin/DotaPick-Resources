import contextlib
import sqlite3
from pathlib import Path

import settings
from model import Hero, Role, Filter, SkillLevel
from utils import get_db_dir


def get_basic_hero_list_from_db():
    """ Return List[Hero] with basic info from hero table. """

    hero_list = []
    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()
        curs.execute("""SELECT id, dotabuff_name, name, update_date FROM hero""")

        result = curs.fetchall()
        hero_list = [Hero(id_=hero_info_tuple[0],
                          dotabuff_name=hero_info_tuple[1],
                          name=hero_info_tuple[2],
                          update_date=hero_info_tuple[3]) for hero_info_tuple in result]

    return hero_list


def get_role_list_from_db():
    """ Return List[role] with basic info from role table. """

    role_list = []
    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()
        curs.execute("""SELECT id, name FROM role""")

        result = curs.fetchall()
        role_list = [Role(id_=hero_info_tuple[0],
                          name=hero_info_tuple[1]) for hero_info_tuple in result]

    return role_list


def get_filter_list_from_db():
    """ Return List[filter] with basic info from filter table. """

    filter_list = []
    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()
        curs.execute("""SELECT id, name FROM filter""")

        result = curs.fetchall()
        filter_list = [Filter(id_=data_tuple[0],
                              name=data_tuple[1]) for data_tuple in result]

    return filter_list


def get_skill_level_list_from_db():
    """ Return List[skill_level] with basic info from skill_level table. """

    skill_level = []
    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()
        curs.execute("""SELECT id, name FROM skill_level""")

        result = curs.fetchall()
        skill_level = [SkillLevel(id_=data_tuple[0],
                                  name=data_tuple[1]) for data_tuple in result]

    return skill_level
