import sys

import databus

try:
    collection_url = sys.argv[1]
except IndexError:
    raise ValueError("No collection url given.")

databus.download_collection(collection_url)
