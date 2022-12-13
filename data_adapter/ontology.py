import json
import logging
import pathlib
from typing import Union


def get_metadata(metadata: Union[str, pathlib.Path, dict]):
    if isinstance(metadata, dict):
        return metadata
    with open(metadata, "r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def get_subject(metadata):
    metadata = get_metadata(metadata)
    if "subject" not in metadata:
        logging.warning(f"No subject found in metadata for table '{metadata['name']}'.")
        return metadata["name"]
    return get_name_from_subject_or_isabout(metadata["subject"])


def get_name_from_subject_or_isabout(field):
    names = []
    for entry in field:
        # pylint: disable=W0511
        # FIXME: Read name from ontology if OEO is present in "path"
        names.append(entry["name"])
    return "_".join(names)
