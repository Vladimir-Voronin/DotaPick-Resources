import datetime
import json
import os
from pathlib import Path

import settings
from db_api.create_db import create_db_and_tables, delete_db
from db_api.update_db import fill_hero_table_from_scratch, fill_skill_level_table_from_scratch, \
    fill_filter_table_from_scratch, fill_role_table_from_scratch, update_role_table, update_hero_winrate_table, \
    update_hero_winrate_matrix_table, update_ally_table
from parsing.parsing_ import get_list_of_hero_only_names, assign_roles_set_for_hero_list, get_filters, \
    download_default_images_for_hero_list
from utils import get_root_dir, get_db_dir, get_hero_images_dir
from git import Repo


def update_info_json(update_name, update_type, description=''):
    date_and_time = str(datetime.datetime.now())
    with open(get_root_dir() / Path(settings.UPDATE_INFO_JSON_FILE_NAME), 'r') as file:
        json_dict = json.load(file)

    with open(get_root_dir() / Path(settings.UPDATE_INFO_JSON_FILE_NAME), 'w') as file:
        json_dict[update_name] = {'update_type': update_type,
                                  'datetime': date_and_time,
                                  'description': description}
        json.dump(json_dict, file)


def update_info_full_db_update(description=''):
    update_info_json('db update', 'full db update', description)


def update_info_db_winrates_update(description=''):
    update_info_json('db update', 'db winrates update', description)


def update_info_hero_images_update(description=''):
    update_info_json('hero images update', 'hero images update', description)


def _create_db_from_scratch():
    delete_db()
    create_db_and_tables()


def update_full_db():
    try:
        _create_db_from_scratch()
        fill_hero_table_from_scratch()
        fill_skill_level_table_from_scratch()
        fill_filter_table_from_scratch()

        hero_list = get_list_of_hero_only_names()
        assign_roles_set_for_hero_list(hero_list)

        fill_role_table_from_scratch(hero_list)

        update_role_table(hero_list)

        update_hero_winrate_table()
        update_hero_winrate_matrix_table()
        update_ally_table()
    except:
        print("Error")
        raise
    else:
        update_info_full_db_update()


def update_winrates_in_db():
    try:
        update_hero_winrate_table()
        update_hero_winrate_matrix_table()
    except:
        raise
    else:
        update_info_db_winrates_update()


def download_images():
    try:
        hero_list = get_list_of_hero_only_names()
        download_default_images_for_hero_list(hero_list)
    except:
        raise
    else:
        update_info_hero_images_update()


def commit_and_push_db_github():
    def git_push():
        try:
            repo = Repo(str(get_root_dir()))
            repo.git.add(get_db_dir(), update=True)
            repo.git.add(get_root_dir() / Path(settings.UPDATE_INFO_JSON_FILE_NAME), update=True)
            repo.index.commit('db update')
            origin = repo.remote(name='origin')
            origin.push()
        except:
            print('Some error occured while pushing the code')
            raise

    git_push()


def commit_and_push_images_github():
    def git_push():
        try:
            repo = Repo(str(get_root_dir()))
            repo.git.add(get_hero_images_dir(), update=True)
            repo.index.commit('hero images update')
            origin = repo.remote(name='origin')
            origin.push()
        except:
            print('Some error has occured while pushing the code')
            raise

    git_push()


if __name__ == '__main__':
    pass
