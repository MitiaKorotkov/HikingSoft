from datetime import timedelta, date
from collections import defaultdict


# =========== Google API

# TODO(Dima): Положить в секретное место. .env?
GOOGLE_CREDENTIALS_PATH = "./GoogleDriveApi/credentials.json"
GOOGLE_TOKEN_PATH = "./GoogleDriveApi/token.json"

#-----------------------------

LINKS = {
    'marshrutka': "https://docs.google.com/spreadsheets/d/1NuvyErjdOtANxOze-8kchGq4mlL0spxEZWMIiec28gM/edit?gid=1050086068#gid=1050086068",
    'photos': "https://drive.google.com/drive/folders/1Hywmx1x1sYioY19JxGJWzd4KVcSX1lWc?usp=sharing",
    'menu': 'https://docs.google.com/spreadsheets/d/1ifwYwXPn6rwr6rKPA2MyTeAwJXjEw20fO-Sr9mILXto/edit?gid=376947626#gid=376947626',
}

TEX_FILENAMES = {
    'preambule': "preambule.tex",
    'fstr_logo': "FSTR_logo.png",
    'fstm_logo': "FSTM_logo.png",
    'moscow_marshrutka_version': "moscow_template.tex",
    'region_marshrutka_version': "template.tex",
    'stickers_table': 'stickers_template.tex', # TODO(Dima): поменять на .tex
    'stickers_table_row': 'stickers_row_template.tex',
}

DATA_DIR = './Data'
TMP_FILES_DIR = f'{DATA_DIR}/tmp'
OUT_PDF_FILES_DIR = f'{DATA_DIR}/pdf'
TEX_FILES_DIR = f'{DATA_DIR}/tex_files'

OUT_MARSHRUTKA_FILENAME = 'Маршрутка.pdf'

OUT_STICKERS_FILENAME = 'стикеры.pdf'

ROW_PHOTOS_DIR = DATA_DIR
OUT_PHOTOS_DIR = DATA_DIR

DEFAULT_DATE = "2024:06:30 11:06:40"
START_DATE = "2023-08-13"
FINISH_DATE = "2023-08-31"

start_day = date.fromisoformat(START_DATE)
finish_day = date.fromisoformat(FINISH_DATE)

K = finish_day - start_day

DAY_TO_DATE = {
    f"День {i + 1}": day
    for i, day in enumerate([start_day + timedelta(days=j) for j in range(K.days)])
}
DEFAULT_PHOTO_DIR_NAME = 'НЕСОРТИРОВАННОЕ'
DATE_TO_DAY = defaultdict(
    lambda: DEFAULT_PHOTO_DIR_NAME,
    {
        day: f"День {i + 1}"
        for i, day in enumerate([start_day + timedelta(days=j) for j in range(K.days)])
    },
)

AVAILABLE_IMAGE_EXTENTIONS = ["jpg", "jpeg", "png"]  #  , "heic"]