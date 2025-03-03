import os
import pathlib
import sys

if "COLLECTIONS_DIR" not in os.environ and not (pathlib.Path(os.curdir) / "collections").exists():
    os.environ["COLLECTIONS_DIR"] = str(pathlib.Path(os.curdir))
if "STRUCTURES_DIR" not in os.environ and not (pathlib.Path(os.curdir) / "structures").exists():
    os.environ["STRUCTURES_DIR"] = str(pathlib.Path(os.curdir))

from data_adapter import databus, preprocessing


def download_collection():
    collection_url = input("Enter collection URL: ")
    databus.download_collection(collection_url)


def get_process(collection, process, links):
    df = preprocessing.get_process(collection, process, links)
    print(df)


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "get_process":
        get_process(sys.argv[2], sys.argv[3], sys.argv[4])
    if command == "download":
        download_collection()
