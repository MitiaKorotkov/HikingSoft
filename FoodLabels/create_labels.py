import pandas as pd
import numpy as np

from jinja2 import Environment, FileSystemLoader
import subprocess
import shutil
from pathlib import Path

from constants import (
    TEX_FILES_DIR,
    TEX_FILENAMES,
    OUT_PDF_FILES_DIR,
    OUT_STICKERS_FILENAME,
)

RU_MONTH = {
    1: "Января",
    2: "Февраля",
    3: "Марта",
    4: "Апреля",
    5: "Марта",
    6: "Июня",
    7: "Июля",
    8: "Августа",
    9: "Сентября",
    10: "Октября",
    11: "Ноября",
    12: "Декабря",
}


def prepare_data(raskladka, page="Раскладка"):
    bad_columns = [
        "Unnamed: 1",
        "Дата",
        "Unnamed: 34",
        "Unnamed: 35",
        "Unnamed: 36",
        "Unnamed: 37",
        "Unnamed: 38",
    ]
    bad_rows = [1, 2, 3, 123]

    data = pd.read_excel(raskladka, sheet_name=page)
    data = data.drop(bad_columns, axis=1)
    data = data.drop(bad_rows)
    data = data[data["Продукт"].notna()]
    data = data.reset_index()
    data = data.drop(["index"], axis=1)

    eating_pos = data["Прием пищи"].notna().values
    eating_pos[-1] = True
    eating_inds = np.arange(len(eating_pos))[eating_pos]  # type: ignore
    eating_inds[-1] += 1

    eatings = data["Прием пищи"][eating_pos].values  # type: ignore
    new_eatings = []
    for i, e in enumerate(eatings[:-1]):
        for _ in range(eating_inds[i + 1] - eating_inds[i]):
            new_eatings.append(e)

    data["Прием пищи"] = pd.Series(new_eatings)

    return data


def create_titles(data, circle):
    circle_titles = []
    empty_dict = {
        "eating": "empty",
        "product": "empty",
        "date": "0 декабря",
        "mass": 0,
    }

    circ_data = data[["Прием пищи", "Продукт", *pd.to_datetime(circle), "кол-во чел"]]
    for _, row in circ_data.iterrows():
        dates = list(map(str, row[2:].dropna().index))
        masses = row[2:-1].dropna().values * row[-1]

        for date, mass in zip(dates, masses):
            circle_titles.append(
                {
                    "eating": row[0],
                    "product": row[1],
                    "date": f"{pd.to_datetime(date).day} {RU_MONTH[pd.to_datetime(date).month]}",
                    "mass": int(mass),
                }
            )

    circle_titles = circle_titles + [empty_dict] * (len(circle_titles) % 3)

    triplets = [
        [*circle_titles[i : i + 3]] for i in range(0, len(circle_titles) - 2, 3)
    ]
    return triplets


def write_titles_to_pdf(titles, circle):
    environment = Environment(
        loader=FileSystemLoader("./"),
        comment_start_string="{=",
        comment_end_string="=}",
    )

    preambule_path = Path(TEX_FILES_DIR, TEX_FILENAMES['preambule']).as_posix()
    tmp_tex_file_dir = Path(TEX_FILES_DIR, "tmp")
    tmp_tex_filename = Path(TEX_FILES_DIR, f"{circle}_кольцо.tex")
    tmp_pdf_filename = Path(tmp_tex_file_dir, f"{circle}_кольцо_" + OUT_STICKERS_FILENAME)
    out_pdf_filename = Path(OUT_PDF_FILES_DIR, f"{circle}_кольцо_" + OUT_STICKERS_FILENAME)

    table_template_path = Path(TEX_FILES_DIR, TEX_FILENAMES['stickers_table'].replace('.tex', '.txt')).as_posix()
    table_row_template_path = Path(TEX_FILES_DIR, TEX_FILENAMES['stickers_table_row'].replace('.tex', '.txt')).as_posix()
    Path.rename(Path(table_template_path.replace('.txt', '.tex')), table_template_path)
    Path.rename(Path(table_row_template_path.replace('.txt', '.tex')), table_row_template_path)

    table = []
    for a, b, c in titles:
        data_part = {
            "eating": [a["eating"], b["eating"], c["eating"]],
            "product": [a["product"], b["product"], c["product"]],
            "date": [a["date"], b["date"], c["date"]],
            "mass": [a["mass"], b["mass"], c["mass"]],
        }
        template = environment.get_template(table_row_template_path)
        table_part = template.render(data=data_part)

        table.append(table_part)

    table = "\n".join(table)

    with open(tmp_tex_filename, "w", encoding="utf-8") as file:
        template = environment.get_template(table_template_path)
        table = template.render(preambule=preambule_path, table=table)
        file.write(table)

    PDFTEX_COMPILE_FLAGS = f"-jobname={str(tmp_pdf_filename).removesuffix('.pdf')}"  # + ' -interaction=nonstopmode' # + ' -draftmode'
    subprocess.call(f"pdflatex {PDFTEX_COMPILE_FLAGS} {tmp_tex_filename}")

    if Path.exists(out_pdf_filename):
        Path.unlink(out_pdf_filename)
    Path.rename(tmp_pdf_filename, out_pdf_filename)

    if Path.exists(tmp_tex_file_dir):
        shutil.rmtree(tmp_tex_file_dir)
    Path.unlink(tmp_tex_filename)

    Path.rename(Path(table_template_path), table_template_path.replace('.txt', '.tex'))
    Path.rename(Path(table_row_template_path), table_row_template_path.replace('.txt', '.tex'))


# TODO(Dima): Удалить после тестирования
# def create_titles(data, circle):
#     titles = []
#     circ_data = data[["Прием пищи", "Продукт", *pd.to_datetime(circle), "кол-во чел"]]
#     for _, row in circ_data.iterrows():
#         dates = list(map(str, row[2:].dropna().index))
#         masses = row[2:-1].dropna().values * row[-1]

#         titles.append(
#             {
#                 "eating": row[0],
#                 "product": row[1],
#                 "date/mass": tuple(zip(dates, masses)),
#             }
#         )

#     return titles


# def prepare_triplets(titles):
#     circle_titles = []
#     empty_dict = {
#         "eating": "empty",
#         "product": "empty",
#         "date": '0 декабря',
#         "mass": 0,
#     }

#     for title in titles:
#         for date, mass in title["date/mass"]:
#             pretty_date = (
#                 f"{pd.to_datetime(date).day} {RU_MONTH[pd.to_datetime(date).month]}"
#             )
#             circle_titles.append(
#                 {
#                     "eating": title["eating"],
#                     "product": title["product"],
#                     "date": pretty_date,
#                     "mass": int(mass),
#                 }
#             )
#     circle_titles = circle_titles + [empty_dict] * (len(circle_titles) % 3)

#     triplets = [
#         [*circle_titles[i : i + 3]] for i in range(0, len(circle_titles) - 2, 3)
#     ]
#     return triplets
