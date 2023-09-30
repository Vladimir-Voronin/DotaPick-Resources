from pathlib import Path


def get_root_dir():
    return Path(__file__).parent


def get_resources_dir():
    return get_root_dir() / Path('resources')


def get_db_dir():
    return get_resources_dir() / Path('db')


def get_hero_images_dir():
    return get_resources_dir() / Path('hero_images')


def get_allies_file_path():
    return get_resources_dir() / Path('allies_files/allies')


if __name__ == '__main__':
    print(get_root_dir())
