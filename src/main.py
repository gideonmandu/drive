from dotenv import load_dotenv
from rich import print

from services.get_files import get_files, write_file_to_csv
from services.upload_files import read_files

if __name__ == "__main__":
    load_dotenv()
    # comment function out to add permissions
    read_files(
        email="admin@businesscomtest.com",
        csv_file_name="sample.csv",
    )

    # comment loop out to save shared files data in csv file
    # for file in get_files(email="admin@businesscomtest.com"):
        # write_file_to_csv(file=file, csv_name="sample.csv")
