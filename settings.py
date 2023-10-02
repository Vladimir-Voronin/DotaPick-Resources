DEBUG = True

DB_NAME = 'dotapick.db'
PARSING_NUMBER_OF_WORKERS = 10
PARSING_TIMEOUT = 100

BASE_FILTER_KEYS_FROM_DOTABUFF = [
    'week',
    'month'
]

BASE_SKILL_LEVELS = [
    '<2K MMR',
    '~2K-3k MMR',
    '~3K-4k MMR',
    '~4K-5k MMR',
    '>5K MMR',
]

UPDATE_INFO_JSON_FILE_NAME = 'update-info.json'

DOTABUFF_LINK_PREFIX = r"https://dotabuff.com/"
DOTABUFF_ALL_HEROES_LINK = r"https://dotabuff.com/heroes/"
DOTABUFF_ALL_HEROES_WINRATE_LINK = "https://dotabuff.com/heroes/winning/"
DOTABUFF_COUNTERS_LINK_SUFFIX = r"/counters"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
