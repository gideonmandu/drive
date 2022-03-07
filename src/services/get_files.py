import csv
import os
import json
import logging
from typing import Any
from rich import print
from googleapiclient.errors import HttpError

from services.service import services


logger = logging.getLogger(__name__)


def get_file(email: str, file_id: str) -> dict[str, Any] | None:
    drive_service = services.drive_api_service(user_email=email)
    return drive_service.files().get(
        fileId=file_id,
        supportsAllDrives=True,
        fields="*",
    )


def get_files(
    email: str,
    nextpage_token: str | None = None,
    drive_id: str | None = None,
    page_size: int = 100,
) -> dict | None:
    try:
        drive_service = services.drive_api_service(user_email=email)

        # Call the Drive v3 API
        results = (
            drive_service.files()
            .list(
                pageSize=page_size,
                pageToken=nextpage_token or None,
                fields="*",
                # corpora="drive",
                supportsAllDrives=True,
                # driveId=drive_id or email,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        files: list[dict] = results.get("files", [])
        if token := results.get("nextPageToken"):
            logger.info(print(f"Next page token: {token}"))
            next_files = get_files(
                email=email,
                nextpage_token=token,
            )
            files.extend(list(next_files))
        if not files:
            logger.info(print("No files found."))
            return None
        logger.info(print(f"Total files: {len(files)}"))
        yield from files
    except HttpError as error:
        logger.error(print(f"{error} :raised_eyebrow:"))


def is_empty_file(file_path: str) -> bool:
    return os.path.isfile(file_path) and os.path.getsize(file_path) == 0


def format_json(file: dict[str:Any]) -> None:
    keys_to_remove = (
        "kind",
        "id",
        "starred",
        "trashed",
        "explicitlyTrashed",
        "spaces",
        "version",
        "webContentLink",
        "webViewLink",
        "iconLink",
        "hasThumbnail",
        "thumbnailLink",
        "thumbnailVersion",
        "viewedByMe",
        "viewedByMeTime",
        "createdTime",
        "modifiedTime",
        "modifiedByMeTime",
        "modifiedByMe",
        "lastModifyingUser",
        "ownedByMe",
        "capabilities",
        "viewersCanCopyContent",
        "copyRequiresWriterPermission",
        "writersCanShare",
        "permissionIds",
        "originalFilename",
        "fullFileExtension",
        "fileExtension",
        "md5Checksum",
        "size",
        "quotaBytesUsed",
        "headRevisionId",
        "imageMediaMetadata",
        "isAppAuthorized",
        "linkShareMetadata",
        "exportLinks",
    )
    for k in keys_to_remove:
        try:
            del file[k]
        except KeyError:
            pass


def write_file_to_csv(file: dict[str, Any]) -> None:
    with open(file="sample.csv", mode="a+", encoding="utf-8") as csv_file:
        file_writer = csv.writer(
            csv_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        # adding header if none
        if is_empty_file("sample.csv"):
            file_writer.writerow(
                [
                    "name",
                    "owner",
                    # "role",
                    # "type",
                    # "user",
                    "permissions",
                    "mimetype",
                ]
            )
        try:
            # pick files that are owned by user and are shared
            if (
                file["permissions"]
                and file["ownedByMe"]
                and file["shared"]
                and not file["trashed"]
            ):
                logger.info(print(f"File:-> {file} :page_facing_up:"))
                # format_json(file=file)
                # for permission in file["permissions"]:
                #     file_writer.writerow(
                #         [
                #             file["name"],
                #             file["owners"][0]["emailAddress"],
                #             permission["role"],
                #             permission["type"],
                #             permission["emailAddress"],
                #             file["mimeType"],
                #         ]
                #     )
                file_writer.writerow(
                    [
                        file["name"],
                        file["owners"][0]["emailAddress"],
                        file["permissions"],
                        file["mimeType"],
                    ]
                )
        except KeyError as e:
            logger.error(print(f"{e} :interrobang:"))


def write_file_to_json(file: dict[str, Any], indent: int = 0) -> None:
    with open(file="sample.json", mode="a+", encoding="utf-8") as json_file:
        if is_empty_file("sample.json"):
            json_file.write("[")
        try:
            if (
                file["permissions"]
                and file["ownedByMe"]
                and file["shared"]
                and not file["trashed"]
            ):
                print(file)
                format_json(file=file)
                json.dump(file, json_file, indent=indent)
                json_file.write(",")
        except KeyError as e:
            logger.error(print(f"{e} :interrobang:"))
