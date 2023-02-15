import sys

from data_adapter import databus, preprocessing


def download_collection(collection_url):
    databus.download_collection(collection_url)


def get_process(collection, process):
    df = preprocessing.get_process(collection, process)
    print(df)


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "get_process":
        get_process(sys.argv[2], sys.argv[3])
