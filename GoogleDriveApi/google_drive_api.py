import io
import os.path
from tqdm import tqdm

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from glob import glob
from exif import Image as ExifImage
from PIL import Image

# from pyheif import read_heif

from constants import (
    ROW_PHOTOS_DIR,
    DEFAULT_DATE,
    AVAILABLE_IMAGE_EXTENTIONS,
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_TOKEN_PATH,
)

SCOPES = ["https://www.googleapis.com/auth/drive"]
GOOGLE_TYPES = {
    "folder": "'application/vnd.google-apps.folder'",
    "photo": "application/vnd.google-apps.photo",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

# TODO(Dima): Может, плохая идея
HTTPS_PREFIXIES = {
    'folder': 'https://drive.google.com/drive/folders/',
    'spreadsheet': 'https://docs.google.com/spreadsheets/d/',
}


def get_credentials():
    creds = None

    if os.path.exists(GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_PATH, SCOPES
            )

        creds = flow.run_local_server(port=0)  # type: ignore
        with open(GOOGLE_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


def find_folder(folder_name, credentials, parent_id=None):
    try:
        service = build("drive", "v3", credentials=credentials)
        querry = f"mimeType = {GOOGLE_TYPES['folder']} and name = '{folder_name}'"
        if parent_id:
            querry += f" and '{parent_id}' in parents"
        results = (
            service.files()
            .list(q=querry, pageSize=100, fields="files(id, name)")
            .execute()
        )

        return results.get("files", [])[0]

    except HttpError as error:
        with open("./logs.txt", "a+") as logs:
            logs.write(f"\tError while searching {folder_name}:\t{error}\n")

        return None


# TODO(Dima): Rename?
# TODO(Dima): Regular expr??
def get_folder_id_by_link(link):
    return link.split("/")[-1].split("?")[0]


def get_spreadsheet_id(link:str):
    return link.removeprefix(HTTPS_PREFIXIES['spreadsheet']).split('/')[0]


def files_in_dir(dir_id, credentials, folders_only=False):
    try:
        service = build("drive", "v3", credentials=credentials)
        querry = f"'{dir_id}' in parents"
        if folders_only:
            querry += f" and mimeType = {GOOGLE_TYPES['folder']}"

        results = (
            service.files()
            .list(
                q=querry,
                pageSize=100,
                fields="nextPageToken, files(id, name, imageMediaMetadata)",
            )
            .execute()
        )
        next_page = results.get("nextPageToken", "")

        if not results.get("files", []):
            return results.get("files")

        while next_page:
            next_results = (
                service.files()
                .list(
                    q=querry,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, imageMediaMetadata)",
                    pageToken=next_page,
                )
                .execute()
            )
            next_page = next_results.get("nextPageToken")

            results["files"] += next_results["files"]

        return results.get("files")

    except HttpError as error:
        with open("./logs.txt", "a+") as logs:
            logs.write(f"\tError while scanning {dir_id}:\t{error}\n")

        return []


def bytes_to_image(bytes, path, format):
    bytes.seek(0)

    if format == "heic":
        # bytes = read_heif(bytes) # TODO(Dima): problems with heic
        pi = Image.frombytes(mode=bytes.mode, size=bytes.size, data=bytes.data)
    else:
        pi = Image.open(bytes)

    pi.save(path)


def change_exif(time, path):
    with open(path, "rb") as image:
        image_exif_data = ExifImage(image)

    image_exif_data.set("datetime", time)

    with open(path, "wb") as image:
        image.write(image_exif_data.get_file())


def download_images_from_folder(folder, credentials):
    service = build("drive", "v3", credentials=credentials)
    folder_name = folder.get("name")

    with open("logs.txt", "a+") as logs:
        logs.write(
            f"\n\tIn folder {folder_name.encode('utf-8', 'ignore').decode('cp1251')}:\n"
        )

    downloaded = 0
    skipped = 0
    errors = 0
    for image in tqdm(files_in_dir(folder.get("id"), credentials)):
        # TODO(Dima): maybe make it recursevly for find images in subfolders
        image_extention = image.get("name").split(".")[-1].lower()
        if image_extention not in AVAILABLE_IMAGE_EXTENTIONS:
            with open("logs.txt", "a+") as logs:
                logs.write(
                    f"\t\tCan`t download image ({image.get('name').encode('utf-8', 'ignore').decode('cp1251')}):\textention is not avaliable\n"
                )
            continue

        image_name = "".join([*image.get("name").split(".")[:-1], ".jpeg"])
        image_path = os.path.join(ROW_PHOTOS_DIR, folder_name, image_name)

        if not glob(f"./**/**/{image_name}"):
            try:
                request = service.files().get_media(fileId=image.get("id"))
                image_bytes = io.BytesIO()
                downloader = MediaIoBaseDownload(image_bytes, request)

                done = False
                while done is False:
                    _, done = downloader.next_chunk()

                bytes_to_image(image_bytes, image_path, image_extention)

                downloaded += 1
            except Exception as exception:
                with open("logs.txt", "a+") as logs:
                    logs.write(
                        f"\t\tCan`t download image ({image.get('name')}):\t{exception}\n"
                    )
                errors += 1
        else:
            skipped += 1

        if os.path.exists(image_path):
            metadata = image.get("imageMediaMetadata")
            creation_time = (
                metadata.get("time")
                if metadata and metadata.get("time")
                else DEFAULT_DATE
            )

            change_exif(creation_time, image_path)

    with open("logs.txt", "a+") as logs:
        logs.write(
            "\n"
            + "\t\tTotal:"
            + f"\n\t\t\tSuccessfully:\t{downloaded}"
            + f"\n\t\t\tErrors:\t\t\t{errors}"
            + f"\n\t\t\tSkip:\t\t\t{skipped}\n"
        )


def download_photos(folder_link):
    with open("./logs.txt", "a+") as logs:
        logs.write("-" * 10 + " upload photos errors " + "-" * 10 + "\n")

    try:
        creds = get_credentials()
    except UnboundLocalError:
        os.remove(GOOGLE_TOKEN_PATH)
        creds = get_credentials()
    except Exception as exception:
        with open("logs.txt", "a+") as logs:
            logs.write(f"\tProblems with credentials:\t{exception}\n")

    drive_photo_folder_id = get_folder_id_by_link(folder_link)

    for folder in files_in_dir(drive_photo_folder_id, creds, folders_only=True):  # type: ignore
        print(f"---------------* {folder.get('name')} *---------------")

        path = os.path.join(ROW_PHOTOS_DIR, folder.get("name"))
        if not os.path.isdir(path):
            os.mkdir(path)

        download_images_from_folder(folder, creds)  # type: ignore


def download_table(link, out_filename):
    try:
        creds = get_credentials()
    except UnboundLocalError:
        os.remove(GOOGLE_TOKEN_PATH)
        creds = get_credentials()

    try:
        service = build("drive", "v3", credentials=creds)

        table_id = get_spreadsheet_id(link)

        request = service.files().export_media(
            fileId=table_id, mimeType=GOOGLE_TYPES["excel"]
        )

        fh = io.FileIO(out_filename, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            _, done = downloader.next_chunk()

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
        # TODO(Dima): logging
