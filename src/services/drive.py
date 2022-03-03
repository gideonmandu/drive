import csv
from typing import Any
from .service  import services
from googleapiclient.errors import HttpError


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
        # check if all files are pulled
        if results.get("nextPageToken"):
            next_files = get_files(
                email=email,
                nextpage_token=results.get("nextPageToken"),
            )
            files.append(iter(next_files)) if next_files else None

        if not files:
            print("No files found.")
            return None
        print("Files:")
        for file in files:
            yield file
    except HttpError as error:
        print(f"An error occurred: {error}")


def write_files_to_csv(file: dict[str, Any]) -> None:

    with open(file="sample.csv", mode="a") as csv_file:
        file_writer = csv.writer(
            csv_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        try:
            if file["permissions"] and file["ownedByMe"] and file["shared"]:
                for permission in file["permissions"]:
                    file_writer.writerow(
                        [
                            file["name"],
                            file["owners"][0]["emailAddress"],
                            permission["role"],
                            permission["type"],
                            permission["emailAddress"],
                        ]
                    )
        except KeyError as e:
            print(e)
