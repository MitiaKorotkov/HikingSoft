from pathlib import Path

from GoogleDriveApi.google_drive_api import download_table
from constants import TMP_FILES_DIR

from .create_labels import (
    create_titles,
    write_titles_to_pdf,
    prepare_data,
)


def create_labels(table_path):
    data = prepare_data(table_path)

    # TODO(Dima): Вытащить кольца из раскладки
    circles = [
        [
            "2024-06-30 00:00:00",
            "2024-07-01 00:00:00",
            "2024-07-02 00:00:00",
        ],
        [
            "2024-07-03 00:00:00",
            "2024-07-04 00:00:00",
            "2024-07-05 00:00:00",
            "2024-07-06 00:00:00",
            "2024-07-07 00:00:00",
            "2024-07-08 00:00:00",
        ],
        [
            "2024-07-09 00:00:00",
            "2024-07-10 00:00:00",
            "2024-07-11 00:00:00",
            "2024-07-12 00:00:00",
            "2024-07-13 00:00:00",
        ],
        [
            "2024-07-14 00:00:00",
            "2024-07-15 00:00:00",
            "2024-07-16 00:00:00",
            "2024-07-17 00:00:00",
            "2024-07-18 00:00:00",
        ],
    ]

    for i, circle in enumerate(circles):
        titles = create_titles(data, circle)
        write_titles_to_pdf(titles, i)


def main(link, from_google_drive=True):
    table_path = Path(TMP_FILES_DIR, 'menu.xlsx')

    if from_google_drive:
        download_table(link, table_path)
    else:
        # TODO(Dima): Добавить возможнось брать таблицу с компа
        pass

    create_labels(table_path)

    Path.unlink(table_path)
