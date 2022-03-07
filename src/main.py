from dotenv import load_dotenv
from rich import print

from services.get_files import get_files, write_file_to_csv
from services.upload_files import upload_files, read_files

if __name__ == "__main__":
    load_dotenv()
    read_files(email="admin@businesscomtest.com", csv_file_name="sample.csv")
    # for file in get_files(email="admin@businesscomtest.com"):
    #     # print(f'{file["name"]} ({file["id"]})')
    #     write_file_to_csv(file=file)
