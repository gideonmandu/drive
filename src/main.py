from dotenv import load_dotenv
from rich import print

from services.get_files import get_files, write_file_to_csv
from services.upload_files import read_files

if __name__ == "__main__":
    load_dotenv()
    # comment function call out to add permissions
    read_files(
        email="azeem.aliyar@copiakenya.com",
        csv_file_name="azeem@copiauganda.com.csv",
    )

    # comment for loop out to save shared files data in csv file
    # for file in get_files(email="azeem@copiauganda.com"):
    #     write_file_to_csv(file=file, csv_name="azeem@copiauganda.com.csv")
