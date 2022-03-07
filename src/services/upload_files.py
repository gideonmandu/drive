import csv
import logging
import os
import sys
from typing import Any

from rich import print
from googleapiclient.errors import HttpError, MediaUploadSizeError
from googleapiclient.http import MediaFileUpload

from services.service import services
from services.get_files import get_files

logger = logging.getLogger(__name__)


def check_file_name_in_csv(
    csv_file: str,
    file_name: str,
) -> list[str | dict[str, str]]:
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                # if file_name in row or file_name.split(".")[0] in row:
                if file_name in row:
                    logger.info(print(f"File found :smiley: {row}"))
                    return row
        except csv.Error as e:
            sys.exit(f"file {csv_file}, line {reader.line_num}: {e}")


# Local files Folder Path
path = f"{os.getcwd()}/files"

# Read File name
def read_file_name(file_path: str) -> str:
    file_name = None
    with open(file_path, "r") as f:
        file_name = f.name.split("/")[-1]
        logger.info(print(f"File Name: {file_name} :ok_hand:"))
    return file_name


def callback(request_id, response: dict[str, Any], exception) -> None:
    if exception:
        # Handle error
        logger.error(print(f"{exception} :rotating_light:"))
    else:
        logger.info(
            print(f"UPDATED PERMISSION Id: {response.get('id')} :unlock:"),
        )


def add_permissions(
    file_id: str,
    file_info: list[str | dict[str, str]],
) -> None:
    try:
        drive_service = services.drive_api_service(user_email=file_info[1])
        batch = drive_service.new_batch_http_request(callback=callback)
        # convert string to list with dicts
        for permission in eval(file_info[2]):
            if permission["role"] != "owner":
                user_permission = {
                    "type": permission["type"],
                    "role": permission["role"],
                    "emailAddress": permission["emailAddress"],
                }
                batch.add(
                    drive_service.permissions().create(
                        fileId=file_id,
                        body=user_permission,
                        fields="id",
                        sendNotificationEmail=False,
                        supportsAllDrives=True,
                    )
                )
        batch.execute()
    except TypeError as e:
        logger.fatal(print(f"Error {e} -> file not in sheet :exploding_head:"))


def upload_file(
    file_info: list[str | dict[str, str]],
    file_path: str,
) -> None:
    try:
        drive_service = services.drive_api_service(
            user_email=file_info[1],
        )
    except TypeError as e:
        logger.fatal(print(f"Error {e} :exploding_head:"))

    file_metadata = {
        # added number to differentiate uploaded files
        "name": f"{file_info[0]}2",
        "mimeType": file_info[-1],
    }

    media = MediaFileUpload(
        file_path,
        resumable=True,
    )

    try:
        uploaded = (
            drive_service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="*",
            )
            .execute()
        )
        logger.info(print("FILE ADDED :sweat_smile:"))
        logger.info(print(uploaded))
        add_permissions(file_id=uploaded.get("id"), file_info=file_info)
    except (HttpError, MediaUploadSizeError) as e:
        logger.fatal(print(f"Error {e} :exploding_head:"))


def check_file(
    file_info: list[str | dict[str, str]],
    file_id: str,
) -> None:
    try:
        add_permissions(file_id=file_id, file_info=file_info)
    except (HttpError, MediaUploadSizeError) as e:
        logger.fatal(print(f"Error {e} :exploding_head:"))


# iterate through all file
def upload_files():
    for file in os.listdir(path=path):
        if file:
            file_path = f"{path}/{file}"
            # call read file name function
            name = read_file_name(file_path)
            # step out of current working dir and check for file
            test = check_file_name_in_csv(
                csv_file="sample.csv",
                file_name=name,
            )
            logger.info(print(test))
            upload_file(file_info=test, file_path=file_path)



# iterate through all file
def read_files(email: str, csv_file_name: str):
    for file in get_files(email=email):
        try:
            test = check_file_name_in_csv(
                csv_file=csv_file_name,
                file_name=file.get("name"),
            )
            logger.info(print(test))
            check_file(file_info=test, file_id=file.get("id"))
        except KeyError as e:
            logger.error(print(f"{e} :interrobang:"))