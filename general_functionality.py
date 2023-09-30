from db_api.create_db import create_db_and_tables, delete_db
from db_api.update_db import fill_hero_table_from_scratch, fill_skill_level_table_from_scratch, \
    fill_filter_table_from_scratch, fill_role_table_from_scratch, update_role_table, update_hero_winrate_table, \
    update_hero_winrate_matrix_table, update_ally_table
from parsing.parsing_ import get_list_of_hero_only_names, assign_roles_set_for_hero_list, get_filters, \
    download_default_images_for_hero_list


def _create_db_from_scratch():
    delete_db()
    create_db_and_tables()


def update_full_db():
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


def update_winrates_in_db():
    update_hero_winrate_table()
    update_hero_winrate_matrix_table()


def download_images():
    hero_list = get_list_of_hero_only_names()
    download_default_images_for_hero_list(hero_list)


if __name__ == '__main__':
    update_winrates_in_db()
