import logging
import os
import pathlib

import sqlalchemy as sa

DEBUG = os.environ.get("DEBUG", "false") == "true"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

ROOT_DIR = pathlib.Path(__file__).parent.parent
COLLECTIONS_DIR = (
    pathlib.Path(os.environ["COLLECTION_DIR"].parent)
    if "COLLECTION_DIR" in os.environ
    else pathlib.Path(__file__).parent.parent / "collections"
)
COLLECTION_JSON = "collection.json"
COLLECTION_META_VERSION = "v1"

STRUCTURES_DIR = (
    pathlib.Path(os.environ["STRUCTURES_DIR"])
    if "STRUCTURES_DIR" in os.environ
    else pathlib.Path(__file__).parent.parent / "structures"
)

DATABUS_ENDPOINT = "https://energy.databus.dbpedia.org/sparql"
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    engine = sa.create_engine(DATABASE_URL)
