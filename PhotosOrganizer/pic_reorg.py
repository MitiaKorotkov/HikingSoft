import os
from datetime import date, time

# from exif import Image
from PIL import Image

from constants import ROW_PHOTOS_DIR, DEFAULT_DIR, DATE_TO_DAY, OUTPUT_DIR, DAY_TO_DATE


def create_folders():
    necessary_dirs = [ROW_PHOTOS_DIR] + [
        os.path.join(OUTPUT_DIR, 'days', day) for day in ["", DEFAULT_DIR, *DAY_TO_DATE.keys()]
    ]

    for d in necessary_dirs:
        if not os.path.exists(d):
            os.mkdir(d)


def photo_name_template(day_number, prefix=""):
    return f"{prefix}{day_number}.jpeg"


def organize_photos_into_folders():
    with open("./logs.txt", "a+") as logs:
        logs.write(
            "\n" + "-" * 10 + " organize photos into folders errors " + "-" * 10 + "\n"
        )

    for root, _, files in os.walk(ROW_PHOTOS_DIR):
        for file in files:
            old_image_path = os.path.join(root, file)

            with Image.open(old_image_path) as image:
                image.load()  # TODO(Dima): maybe not nessesery. only for .png metadate
                exif_datetime = image.getexif().get(306)
                if exif_datetime is None:
                    exif_datetime = ''
                # TODO(Dima): mayby do it more explicitly. Find DateTime in tags???

                try:
                    day = DATE_TO_DAY[
                        date.fromisoformat(exif_datetime.split()[0].replace(":", "-"))
                    ]
                    new_image_path = os.path.join(OUTPUT_DIR, "days", day, file)
                    os.rename(old_image_path, new_image_path)
                except Exception as exception:
                    with open("./logs.txt", "a+") as logs:
                        logs.write(
                            "\t"
                            + f"Couldn't move {old_image_path} to {new_image_path} with exception:\t{exception}\n" # type: ignore
                        )

    not_moved = 0
    for _, _, files in os.walk(ROW_PHOTOS_DIR):
        not_moved += len(files)

    with open("./logs.txt", "a+") as logs:
        logs.write(f"\tTotal not moved:\t{not_moved}\n")

    return
    # NOTE(Dima): version with exif lib
    for root, _, files in os.walk(ROW_PHOTOS_DIR):
        for file in files:
            old_image_path = os.path.join(root, file)

        with open(old_image_path, "rb") as image_file:
            image = Image(image_file)

        try:
            day = DATE_TO_DAY[
                date.fromisoformat(image.datetime.split()[0].replace(":", "-"))
            ]
            new_image_path = os.path.join(OUTPUT_DIR, "days", day, file)
            os.rename(old_image_path, new_image_path)

        except Exception as exception:
            with open("./logs.txt", "a+") as logs:
                logs.write(f"{old_image_path}\t|\t{exception.__repr__()}\n")

    not_moved = 0
    for _, _, files in os.walk(ROW_PHOTOS_DIR):
        not_moved += len(files)

    with open("./logs.txt", "a+") as logs:
        logs.write(f"I couldn't move {not_moved} files\n")


def rename_photos():
    with open("./logs.txt", "a+") as logs:
        logs.write("\n" + "-" * 10 + " rename errors " + "-" * 10 + "\n")

    for root, _, files in os.walk(os.path.join(OUTPUT_DIR, "days")):
        time_and_name = []
        for file in files:
            if root.endswith(DEFAULT_DIR):
                break
            image_path = os.path.join(root, file)

            with Image.open(image_path) as image:
                image.load()  # TODO(Dima): maybe not nessesery. only for .png metadate
                exif_datetime = image.getexif().get(306)
                if exif_datetime is None:
                    exif_datetime = ''
                # TODO(Dima): mayby do it more explicitly. Find DateTime in tags???

                try:
                    creation_time = time.fromisoformat(exif_datetime.split()[-1])
                    time_and_name.append((creation_time, image_path))
                except Exception as exception:
                    with open("./logs.txt", "a+") as logs:
                        logs.write(
                            "\t"
                            + f"Couldn't change exif data of {image_path} image with exception:\t{exception}\n"
                        )

        for day_number, (_, old_image_path) in enumerate(
            sorted(time_and_name), start=1
        ):
            new_image_path = os.path.join(root, photo_name_template(day_number))
            if not os.path.exists(new_image_path):
                os.rename(old_image_path, new_image_path)
        # TODO(Dima): Bug here!!! problem with second try when some photos already sorted

    # TODO(Dima): maybe add version with exif lib
