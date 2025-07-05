from pathlib import Path

from MarshrutkaCompliter.main import main as marshrutka_complite
# from PhotosOrganizer.main import main as organize_photos
from FoodLabels.main import main as create_stickers

from constants import LINKS, DATA_DIR, TMP_FILES_DIR, OUT_PDF_FILES_DIR
# TODO(Dima): Разобраться с константами. Dataclass?
# TODO(Dima): Сделать нормальное логирование
if __name__ == "__main__":
    if not Path.exists(Path(DATA_DIR)):
        Path.mkdir(Path(DATA_DIR))
    if not Path.exists(Path(TMP_FILES_DIR)):
        Path.mkdir(Path(TMP_FILES_DIR))
    if not Path.exists(Path(OUT_PDF_FILES_DIR)):
        Path.mkdir(Path(OUT_PDF_FILES_DIR))
    # link = input()

    marshrutka_link = LINKS['marshrutka']
    photos_link = LINKS['photos']
    menu_link = LINKS['menu']

    marshrutka_complite(marshrutka_link)
    # organize_photos(photos_link, rename=True)
    # create_stickers(menu_link)
