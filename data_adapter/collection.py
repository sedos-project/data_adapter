import json
import pathlib
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Union

from data_adapter import core, ontology, settings


class CollectionError(Exception):
    """Raised if collection data or metadata is invalid"""


class DataType(IntEnum):
    Scalar = 0
    Timeseries = 1


@dataclass
class Artifact:
    collection: str
    group: str
    artifact: str
    version: str
    filename: Optional[str] = None
    subject: Optional[str] = None
    datatype: DataType = DataType.Scalar

    @property
    def path(self):
        return settings.COLLECTIONS_DIR / self.collection / self.group / self.artifact / self.version

    @property
    def metadata(self):
        filename = self.filename
        if not filename:
            for file in self.path.iterdir():
                filename = file.stem
                break
        with open(self.path / f"{filename}.json", "r", encoding="utf-8") as metadata_file:
            return json.load(metadata_file)


def check_collection_meta(collection_meta: dict):
    """
    Simple checks if collection metadata is up-to-date

    Parameters
    ----------
    collection_meta: dict
        Metadata of collection

    Raises
    ------
    CollectionError
        if Collection metadata is invalid
    """
    if collection_meta.get("version", None) != settings.COLLECTION_META_VERSION:
        raise CollectionError("Collection metadata is outdated. Please re-download collection and try again.")
    # Check if artifact info keys are missing:
    for group, artifacts in collection_meta["artifacts"].items():
        for artifact, artifact_infos in artifacts.items():
            for key in ("latest_version",):
                if key not in artifact_infos:
                    raise CollectionError(
                        f"Collection metadata is invalid ({group=}, {artifact=} misses {key=}). "
                        "Collection metadata may changed. Please re-download collection and try again."
                    )


def infer_collection_metadata(collection: str):
    """
    Interferes downloaded collection and updates names and subjects of artifacts in collection metadata file

    Parameters
    ----------
    collection : str
        Name of collection to get metadata from
    """
    collection_meta = get_collection_meta(collection)

    for group_name, artifacts in collection_meta["artifacts"].items():
        for artifact_name in artifacts:
            version = collection_meta["artifacts"][group_name][artifact_name]["latest_version"]

            artifact = Artifact(collection, group_name, artifact_name, version)
            metadata = artifact.metadata
            collection_meta["artifacts"][group_name][artifact_name]["name"] = metadata["name"]
            collection_meta["artifacts"][group_name][artifact_name]["subject"] = ontology.get_subject(metadata)
            collection_meta["artifacts"][group_name][artifact_name]["datatype"] = get_data_type(metadata)

    collection_meta_filename = pathlib.Path(settings.COLLECTIONS_DIR) / collection / "collection.json"
    with collection_meta_filename.open("w", encoding="utf-8") as collection_meta_file:
        json.dump(collection_meta, collection_meta_file)


def get_data_type(metadata: Union[str, pathlib.Path, dict]):
    metadata_dict: dict = core.get_metadata(metadata)
    for field in metadata_dict["resources"][0]["schema"]["fields"]:
        if field["name"].startswith("timeindex"):
            return DataType.Timeseries
    return DataType.Scalar


def get_collection_meta(collection: str) -> dict:
    """
    Returns collection meta file if present

    Parameters
    ----------
    collection : str
        Name of collection to get metadata from

    Returns
    -------
    dict
        Metadata for given collection

    Raises
    ------
    FileNotFoundError
        if collection metadata cannot be found in given collection folder
    """
    collection_folder = pathlib.Path(settings.COLLECTIONS_DIR) / collection
    collection_meta_file = collection_folder / settings.COLLECTION_JSON
    if not collection_meta_file.exists():
        raise FileNotFoundError(
            f"Could not find collection meta ('{settings.COLLECTION_JSON}') in collection folder '{collection_folder}'."
        )
    with open(collection_meta_file, "r", encoding="utf-8") as meta_file:
        metadata = json.load(meta_file)
    check_collection_meta(metadata)
    return metadata


def get_artifacts_from_collection(collection: str, process: Optional[str] = None) -> List[Artifact]:
    """
    Returns list of artifacts belonging to given process (subject)

    Parameters
    ----------
    collection: str
        Collection name
    process : Optional[str]
        Name of process to search collection metadata for. If not set, all artifacts will be returned.

    Returns
    -------
    List[ArtifactPath]
        List of artifacts in collection (belonging to given process, if set)
    """
    collection_meta = get_collection_meta(collection)
    artifacts = []
    for group in collection_meta["artifacts"]:
        for artifact, artifact_info in collection_meta["artifacts"][group].items():
            process_name = artifact_info["subject"] if settings.USE_ANNOTATIONS else artifact_info["name"]
            if process and process_name != process:
                continue
            filename = artifact
            artifacts.append(
                Artifact(
                    collection,
                    group,
                    artifact,
                    artifact_info["latest_version"],
                    filename,
                    subject=process,
                    datatype=DataType(artifact_info["datatype"]),
                )
            )
    return artifacts
