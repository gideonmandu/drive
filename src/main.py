from dotenv import load_dotenv
from rich import print
from services.drive import get_files, write_files_to_csv


if __name__ == "__main__":
    load_dotenv()
    for file in get_files(email="admin@businesscomtest.com"):
        print(f'{file["name"]} ({file["id"]})')
        write_files_to_csv(file=file)