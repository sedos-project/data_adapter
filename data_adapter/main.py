import sys

from data_adapter import databus, preprocessing


def download_collection(collection_url):
    databus.download_collection(collection_url)


def get_process(collection, process, links):
    df = preprocessing.get_process(collection, process, links)
    print(df)


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "get_process":
        get_process(sys.argv[2], sys.argv[3], sys.argv[4])
    if command == "download":
        collection_url = input("Enter collection URL: ")
        download_collection(collection_url)
