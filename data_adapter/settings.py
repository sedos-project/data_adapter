import logging
import os
import pathlib

import sqlalchemy as sa

DEBUG = os.environ.get("DEBUG", "False") == "True"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

USE_ANNOTATIONS = os.environ.get("USE_ANNOTATIONS", "False") == "True"

ROOT_DIR = pathlib.Path(__file__).parent.parent
COLLECTIONS_DIR = (
    pathlib.Path(os.environ["COLLECTIONS_DIR"])
    if "COLLECTIONS_DIR" in os.environ
    else pathlib.Path.cwd() / "collections"
)
if not COLLECTIONS_DIR.exists():
    raise FileNotFoundError(
        f"Could not find collections directory '{COLLECTIONS_DIR}'. "
        "You should either create the collections folder or "
        "change path to collection folder by changing environment variable 'COLLECTIONS_DIR'."
    )
COLLECTION_JSON = "collection.json"
COLLECTION_META_VERSION = "v3"

STRUCTURES_DIR = (
    pathlib.Path(os.environ["STRUCTURES_DIR"]) if "STRUCTURES_DIR" in os.environ else pathlib.Path.cwd() / "structures"
)
if not STRUCTURES_DIR.exists():
    raise FileNotFoundError(
        f"Could not find structure directory '{STRUCTURES_DIR}'. "
        "You should either create the structure folder or "
        "change path to structure folder by changing environment variable 'STRUCTURES_DIR'."
    )

DATABUS_ENDPOINT = "https://energy.databus.dbpedia.org/sparql"
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    engine = sa.create_engine(DATABASE_URL)
