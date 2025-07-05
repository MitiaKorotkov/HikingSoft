from GoogleDriveApi.google_drive_api import download_photos
from .pic_reorg import create_folders, organize_photos_into_folders, rename_photos


def main(link, rename=False, from_google_drive=True):
    open("./logs.txt", "w")

    create_folders()

    if from_google_drive:
        download_photos(link)
    else:
        # TODO(Dima): Добавить возможность выбрать папку на компе и работать с ней
        pass 
    
    organize_photos_into_folders()

    if rename:
        rename_photos()

