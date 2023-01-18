import logging
import pathlib
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from typing import Generator, Union

from data_adapter import collection, core


class AnnotationQuality(IntEnum):
    NoAnnotation = 0
    NameAnnotation = 1
    OEOAnnotation = 2


@dataclass
class Annotation:
    field: str
    quality: AnnotationQuality


class AnnotationError(Exception):
    """Raised if annotation is corrupted"""


def get_subject(metadata: Union[str, pathlib.Path]) -> str:
    metadata = core.get_metadata(metadata)
    if "subject" not in metadata:
        return metadata["name"]
    return get_name_from_annotation(metadata["subject"], default=metadata["name"])


def get_name_from_ontology(oeo_path: str) -> str:
    """
    Looks up ontology API and returns name of concept

    Parameters
    ----------
    oeo_path: str
        URL to ontology concept

    Returns
    -------
    str
        Name of concept

    Raises
    ------
    AnnotationError
        If concept is not found
    """
    # pylint: disable=W0125
    if False:
        # pylint: disable=W0511
        return oeo_path  # FIXME: Read name from ontology
    raise AnnotationError(f"No ontology concept found for {oeo_path=}.")


def get_name_from_annotation(annotation, default) -> str:
    names = []
    if not annotation:
        return default
    for entry in annotation:
        if "path" in entry:
            try:
                names.append(get_name_from_ontology(entry["path"]))
                continue
            except AnnotationError:
                pass
        if "name" in entry and annotation["name"]:
            names.append(entry["name"])
            continue
        logging.warning(f"Could not read annotation ({annotation=}) for '{default}'.")
        return default
    return "_".join(names)


def __check_quality_of_annotation(
    annotation: list[dict[str, str]]
) -> AnnotationQuality:
    """
    Checks quality for given annotation.

    Parameters
    ----------
    annotation: list[dict[str, str]]
        Annotation (entry from "isAbout" or "subject") dict

    Returns
    -------
    AnnotationQuality
        Annotation quality of given annotation
    """
    qualities = set()
    for entry in annotation:
        if "path" in entry:
            try:
                get_name_from_ontology(entry["path"])
            except AnnotationError:
                pass
            finally:
                qualities.add(AnnotationQuality.OEOAnnotation)
        elif "name" in entry and entry["name"]:
            qualities.add(AnnotationQuality.NameAnnotation)
        else:
            qualities.add(AnnotationQuality.NoAnnotation)
    if len(qualities) == 1:
        return qualities.pop()
    return AnnotationQuality(min(quality.value for quality in qualities))


def check_annotations_in_metadata(metadata: dict) -> Generator[Annotation, None, None]:
    """
    Checks annotations for every field+subject in given metadata

    Parameters
    ----------
    metadata: dict
        Metadata

    Yields
    -------
    Annotation
        includes name of annotation and its quality
    """
    if "subject" not in metadata:
        yield Annotation("subject", AnnotationQuality.NoAnnotation)
    else:
        yield Annotation("subject", __check_quality_of_annotation(metadata["subject"]))
    for field in metadata["resources"][0]["schema"]["fields"]:
        if "isAbout" not in field:
            yield Annotation(field["name"], AnnotationQuality.NoAnnotation)
        else:
            yield Annotation(
                field["name"], __check_quality_of_annotation(field["isAbout"])
            )


def check_annotations_in_collection(
    collection_name: str,
) -> dict[str, list[Annotation]]:
    """
    Checks annotations for every field+subject in artifacts of given collection.

    Parameters
    ----------
    collection_name: str
        Name of collection to check annotations for.

    Returns
    -------
    dict[str, list[Annotation]]
        Dictionary of artifacts (key) with its annotations and annotation quality for each field and subject.
    """

    annotation_qualities = defaultdict(list)
    artifacts = collection.get_artifacts_from_collection(collection_name)
    for artifact in artifacts:
        metadata = collection.get_metadata_from_artifact(artifact)
        annotation_qualities[artifact].extend(*check_annotations_in_metadata(metadata))
    return annotation_qualities
