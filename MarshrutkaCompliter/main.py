from pathlib import Path
import shutil
import subprocess
from jinja2 import Environment, FileSystemLoader

from constants import (
    TEX_FILENAMES,
    TEX_FILES_DIR,
    OUT_MARSHRUTKA_FILENAME,
    OUT_PDF_FILES_DIR,
    TMP_FILES_DIR,
)
from .parse_table import parse_table
from GoogleDriveApi.google_drive_api import download_table


# TODO(Dima): Поправить задание путей
# TODO(Dima): logging
def fill_template(table_path, version):
    pictures_path = {
        'FSTR_logo': Path(TEX_FILES_DIR, TEX_FILENAMES['fstr_logo']).as_posix(),
        'FSTM_logo': Path(TEX_FILES_DIR, TEX_FILENAMES['fstm_logo']).as_posix(),
    }
    preambule_path = Path(TEX_FILES_DIR, TEX_FILENAMES['preambule']).as_posix()

    tmp_tex_files_dir = Path(TEX_FILES_DIR, 'tmp')
    tmp_tex_file_path = Path(TEX_FILES_DIR, 'tmp_marshrutka.tex')
    match version:
        case 'Moscow':
            tex_template_path = Path(TEX_FILES_DIR, TEX_FILENAMES['moscow_marshrutka_version'])
        case 'Region':
            tex_template_path = Path(TEX_FILES_DIR, TEX_FILENAMES['region_marshrutka_version'])

    txt_template_path = tex_template_path.as_posix().replace(".tex", ".txt") # type: ignore
    tmp_pdf_file_path = Path(tmp_tex_files_dir, OUT_MARSHRUTKA_FILENAME)
    out_pdf_file_path = Path(OUT_PDF_FILES_DIR, OUT_MARSHRUTKA_FILENAME)

    shutil.copyfile(tex_template_path, txt_template_path) # type: ignore

    with open(tmp_tex_file_path, "w", encoding="utf-8") as file:
        general_info, tables, weights = parse_table(table_path, version)

        environment = Environment(
            loader=FileSystemLoader("./"),
            block_start_string="{~",
            block_end_string="~}",
            comment_start_string="{=",
            comment_end_string="=}",
        )
        template = environment.get_template(txt_template_path)
        marshrutka = template.render(
            pictures=pictures_path,
            preambule=preambule_path,
            general_info=general_info,
            tables=tables,
            weights=weights,
        )
        file.write(marshrutka)

    PDFTEX_COMPILE_FLAGS = f"-jobname={str(tmp_pdf_file_path).removesuffix('.pdf')}"  # + ' -interaction=nonstopmode' # + ' -draftmode'
    subprocess.call(f"pdflatex {PDFTEX_COMPILE_FLAGS} {tmp_tex_file_path}")

    if Path.exists(out_pdf_file_path):
        Path.unlink(out_pdf_file_path)
    Path.rename(tmp_pdf_file_path, out_pdf_file_path)

    shutil.rmtree(tmp_tex_files_dir)
    # Path.unlink(tmp_tex_file_path)
    Path.unlink(Path(txt_template_path))
    # TODO(Dima): Добавить возможность сохранять тех файл в режиме отладки?


def main(link, version='Moscow', from_google_drive=True):
    table_path = Path(TMP_FILES_DIR, 'marshrutka_data.xlsx')

    if from_google_drive:
        download_table(link, table_path)
    else:
        # TODO(Dima): Добавить возможнось брать таблицу с компа
        pass
    
    fill_template(table_path, version)

    Path.unlink(table_path)
