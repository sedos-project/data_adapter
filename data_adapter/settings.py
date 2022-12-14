import logging
import os
import pathlib

DEBUG = os.environ.get("DEBUG", "false") == "true"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

ROOT_DIR = pathlib.Path(__file__).parent.parent
COLLECTIONS_DIR = (
    pathlib.Path(os.environ["COLLECTION_DIR"])
    if "COLLECTION_DIR" in os.environ
    else pathlib.Path.cwd() / "collections"
)
COLLECTION_JSON = "collection.json"

DATABUS_ENDPOINT = "https://energy.databus.dbpedia.org/sparql"
