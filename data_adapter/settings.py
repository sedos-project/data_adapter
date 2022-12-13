import logging
import os
import pathlib

DEBUG = os.environ.get("DEBUG", "false") == "true"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

ROOT_DIR = pathlib.Path(__file__).parent.parent
COLLECTIONS_DIR = ROOT_DIR / "collections"

DATABUS_ENDPOINT = "https://energy.databus.dbpedia.org/sparql"

COLLECTION_JSON = "collection.json"
