import contextlib
import datetime
import logging
import sqlite3
from pathlib import Path

import settings
from db_api.read_db import get_basic_hero_list_from_db, get_role_list_from_db, get_filter_list_from_db, \
    get_skill_level_list_from_db
from parsing.parsing_ import get_list_of_hero_only_names, get_filters, get_general_winrate_by_hero_list, \
    get_dict_for_hero_winrate_matrix
from utils import get_db_dir, get_allies_file_path

logger = logging.getLogger(__name__)


def fill_hero_table_from_scratch():
    """ Get all heroes from dotabuff and insert them into hero table. """

    hero_list = get_list_of_hero_only_names()

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        clean_table_sql = """DELETE FROM hero"""
        curs.execute(clean_table_sql)
        conn.commit()

        logger.info('hero table has been cleaned')

        for hero in hero_list:
            curs.execute(
                f"""INSERT INTO hero(dotabuff_name, name, update_date) 
                    VALUES(?, ?, ?)""",
                (hero.dotabuff_name, hero.name, str(datetime.datetime.now())))

        conn.commit()

        logger.info('hero table has been updated')


def fill_skill_level_table_from_scratch():
    """ Remove records from skill_level table and insert them from scratch. """

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        clean_table_sql = """DELETE FROM skill_level"""
        curs.execute(clean_table_sql)
        conn.commit()

        logger.info('skill_level table has been cleaned')

        for skill_level in settings.BASE_SKILL_LEVELS:
            curs.execute(
                f"""INSERT INTO skill_level(name) 
                    VALUES(?)""",
                (skill_level,))

        conn.commit()

        logger.info('skill_level table has been updated')


def fill_filter_table_from_scratch():
    """ Remove records from filter table and insert them from scratch. """

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        clean_table_sql = """DELETE FROM filter"""
        curs.execute(clean_table_sql)
        conn.commit()

        logger.info('filter table has been cleaned')

        for filter_ in get_filters():
            curs.execute(
                f"""INSERT INTO filter(name) 
                    VALUES(?)""",
                (filter_,))

        conn.commit()

        logger.info('filter table has been updated')


def fill_role_table_from_scratch(hero_list):
    """ Remove records from role table and insert them from scratch. """

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        clean_table_sql = """DELETE FROM role"""
        curs.execute(clean_table_sql)
        conn.commit()

        logger.info('role table has been cleaned')

        for role in set((role for hero in hero_list for role in hero.roles_set)):
            curs.execute(
                f"""INSERT INTO role(name) 
                    VALUES(?)""",
                (role,))

        conn.commit()

        logger.info('role table has been updated')


def update_role_table(hero_list):
    """ Insert or replace roles in hero_roles table """

    hero_list_db = get_basic_hero_list_from_db()
    role_list_db = get_role_list_from_db()

    hero_dict = {hero.dotabuff_name: hero.id for hero in hero_list_db}
    role_dict = {role.name: role.id for role in role_list_db}

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        clean_table_sql = """DELETE FROM hero_role"""
        curs.execute(clean_table_sql)
        conn.commit()

        logger.info('hero_role table has been cleaned')

        insert_role_sql = """INSERT INTO hero_role (hero_id, role_id) VALUES (?, ?)"""

        for hero in hero_list:
            for role in hero.roles_set:
                hero_id = hero_dict[hero.dotabuff_name]
                role_id = role_dict[role]
                curs.execute(
                    insert_role_sql,
                    (hero_id, role_id))

        conn.commit()

        logger.info('hero_role table has been updated')


def update_hero_winrate_table(skill_level=None):
    """ Insert or replace data in hero_winrate table. """

    hero_list = get_list_of_hero_only_names()
    if not skill_level:
        filter_hero_list_dict = get_general_winrate_by_hero_list(hero_list)
    else:
        raise NotImplementedError("Parse by specific skill level isn't implemented yet")

    hero_list_db = get_basic_hero_list_from_db()
    filter_list_db = get_filter_list_from_db()
    skill_level_db = get_skill_level_list_from_db()

    hero_dict = {hero.dotabuff_name: hero.id for hero in hero_list_db}
    filter_dict = {filter_.name: filter_.id for filter_ in filter_list_db}
    skill_level_dict = {sl.name: sl.id for sl in skill_level_db}

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        insert_hero_winrate_sql = """INSERT OR IGNORE INTO hero_winrate (hero_id, filter_id, 
        skill_level_id, winrate, update_date) 
        VALUES (?, ?, ?, ?, ?)"""

        update_hero_winrate_sql = """UPDATE hero_winrate SET winrate = ?, update_date = ? 
                                     WHERE hero_id = ? AND filter_id = ? AND skill_level_id = ?"""
        for filter_ in filter_hero_list_dict.keys():
            for hero in filter_hero_list_dict[filter_]:
                hero_id = hero_dict[hero.dotabuff_name]
                filter_id = filter_dict[filter_]
                skill_level_id = skill_level_dict[skill_level] if skill_level else None
                curs.execute(
                    insert_hero_winrate_sql,
                    (hero_id, filter_id, skill_level_id, hero.general_winrate, datetime.datetime.now()))
                curs.execute(
                    update_hero_winrate_sql,
                    (hero.general_winrate, datetime.datetime.now(), hero_id, filter_id, skill_level_id))

        conn.commit()

        logger.info('hero_winrate table has been updated')


def update_hero_winrate_matrix_table():
    """ Insert or replace data in hero_winrate_matrix table. """

    hero_list = get_list_of_hero_only_names()
    filter_hero_list_dict = get_dict_for_hero_winrate_matrix(hero_list)

    hero_list_db = get_basic_hero_list_from_db()
    filter_list_db = get_filter_list_from_db()

    hero_dict = {hero.dotabuff_name: hero.id for hero in hero_list_db}
    filter_dict = {filter_.name: filter_.id for filter_ in filter_list_db}

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        insert_hero_winrate_matrix_sql = """INSERT OR IGNORE INTO hero_winrate_matrix (hero_id, hero_id_enemy, 
        filter_id, winrate, update_date) 
        VALUES (?, ?, ?, ?, ?)"""

        update_hero_winrate_matrix_sql = """UPDATE hero_winrate_matrix SET winrate = ?, update_date = ? 
                                     WHERE hero_id = ? AND hero_id_enemy = ? AND filter_id = ?"""
        for filter_ in filter_hero_list_dict.keys():
            for hero in filter_hero_list_dict[filter_]:
                for enemy, winrate_against in hero.winrate_dict.items():
                    hero_id = hero_dict[hero.dotabuff_name]
                    hero_id_enemy = hero_dict[enemy.dotabuff_name]
                    filter_id = filter_dict[filter_]
                    curs.execute(
                        insert_hero_winrate_matrix_sql,
                        (hero_id, hero_id_enemy, filter_id, winrate_against, datetime.datetime.now()))
                    curs.execute(
                        update_hero_winrate_matrix_sql,
                        (winrate_against, datetime.datetime.now(), hero_id, hero_id_enemy, filter_id))

        conn.commit()

        logger.info('hero_winrate_matrix table has been updated')


def update_ally_table():
    """ Updating table ally with best allies for every hero. """

    hero_list_db = get_basic_hero_list_from_db()

    hero_dict = {hero.dotabuff_name: hero.id for hero in hero_list_db}
    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(settings.DB_NAME))) as conn:
        curs = conn.cursor()

        clean_table_sql = """DELETE FROM ally"""
        curs.execute(clean_table_sql)
        conn.commit()

        logger.info('ally table has been cleaned')

        insert_ally_sql = """INSERT INTO ally (hero_id, ally_id) VALUES (?, ?)"""

        with open(get_allies_file_path(), 'r') as file:
            for line in file:
                hero_ally = line.split(":")
                hero_ally = [str_.strip() for str_ in hero_ally]
                hero = hero_ally[0]
                allies = hero_ally[1].split(", ")
                for ally in allies:
                    curs.execute(insert_ally_sql, (hero_dict[hero], hero_dict[ally]))
        conn.commit()

        logger.info('ally table has been updated')
