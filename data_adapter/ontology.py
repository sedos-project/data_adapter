import logging

from data_adapter import core


class AnnotationError(Exception):
    """Raised if annotation is corrupted"""


def get_subject(metadata):
    metadata = core.get_metadata(metadata)
    if "subject" not in metadata or len(metadata["subject"]) == 0:
        logging.warning(f"No subject found in metadata for table '{metadata['name']}'.")
        return metadata["name"]
    try:
        return get_name_from_annotation(metadata["subject"])
    except AnnotationError:
        logging.warning(f"No subject found in metadata for table '{metadata['name']}'.")
        return metadata["name"]


def get_name_from_annotation(annotation):
    names = []
    for entry in annotation:
        # pylint: disable=W0511
        # FIXME: Read name from ontology if OEO is present in "path"
        if "name" not in entry:
            raise AnnotationError("No annotation found")
        names.append(entry["name"])
    return "_".join(names)
