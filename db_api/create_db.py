import contextlib
import sqlite3
from pathlib import Path

from settings import DB_NAME
from utils import get_db_dir


def create_db_and_tables():
    """ Create basic tables for dotapick.db. """

    with contextlib.closing(sqlite3.connect(get_db_dir() / Path(DB_NAME))) as conn:
        curs = conn.cursor()

        table_hero_sql = """
            CREATE TABLE hero (
                id integer PRIMARY KEY,
                dotabuff_name TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL, 
                update_date TEXT NOT NULL
            )
        """

        table_skill_level = """
            CREATE TABLE skill_level (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """

        table_filter = """
                CREATE TABLE filter (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """

        table_role = """
                CREATE TABLE role (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """

        table_hero_winrate_sql = """
            CREATE TABLE hero_winrate (
                hero_id INTEGER,
                filter_id INTEGER,
                skill_level_id INTEGER,
                winrate REAL NOT NULL,
                update_date TEXT NOT NULL,
                FOREIGN KEY(hero_id) REFERENCES hero(id),
                FOREIGN KEY(filter_id) REFERENCES filter(id),
                FOREIGN KEY(skill_level_id) REFERENCES skill_level(id),
                UNIQUE(hero_id, filter_id, skill_level_id)
            )
        """

        table_hero_winrate_matrix = """
            CREATE TABLE hero_winrate_matrix (
                hero_id INTEGER,
                hero_id_enemy INTEGER,
                filter_id INTEGER,
                winrate REAL NOT NULL,
                update_date TEXT NOT NULL,
                FOREIGN KEY(hero_id) REFERENCES hero(id),
                FOREIGN KEY(hero_id_enemy) REFERENCES hero(id),
                FOREIGN KEY(filter_id) REFERENCES filter(id),
                UNIQUE(hero_id, hero_id_enemy, filter_id)
            ) 
        """

        table_hero_role_sql = """
            CREATE TABLE hero_role (
                hero_id INTEGER,
                role_id INTEGER,
                FOREIGN KEY(hero_id) REFERENCES hero(id),
                FOREIGN KEY(role_id) REFERENCES role(id),
                UNIQUE(hero_id, role_id)
            )
        """

        table_allies_sql = """
            CREATE TABLE ally (
                hero_id INTEGER,
                ally_id INTEGER,
                FOREIGN KEY(hero_id) REFERENCES hero(id),
                FOREIGN KEY(ally_id) REFERENCES hero(id)
            ) 
        """

        curs.execute(table_hero_sql)
        curs.execute(table_skill_level)
        curs.execute(table_filter)
        curs.execute(table_role)
        curs.execute(table_hero_winrate_sql)
        curs.execute(table_hero_winrate_matrix)
        curs.execute(table_hero_role_sql)
        curs.execute(table_allies_sql)
        conn.commit()


def delete_db():
    """ Delete local db """

    path_to_delete = get_db_dir() / Path(DB_NAME)
    path_to_delete.unlink(missing_ok=False)


if __name__ == '__main__':
    create_db_and_tables()
