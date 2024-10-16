"""Module handles extraction of processes from databus collection."""
import json
import pathlib
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Union

import frictionless
import pandas as pd

from data_adapter import core, ontology, settings


class CollectionError(Exception):
    """Raised if collection data or metadata is invalid."""


class DataType(IntEnum):
    """Distinguishes between scalar and timeseries data type."""

    Scalar = 0
    Timeseries = 1


@dataclass
class Artifact:
    """Holds information on artifact."""

    collection: str
    group: str
    artifact: str
    version: str
    filename: Optional[str] = None
    datatype: DataType = DataType.Scalar
    multiple_types: bool = False

    @property
    def path(self) -> pathlib.Path:
        return settings.COLLECTIONS_DIR / self.collection / self.group / self.artifact / self.version

    @property
    def metadata(self) -> dict:
        with open(self.path / self.get_filename(".json"), encoding="utf-8") as metadata_file:
            return json.load(metadata_file)

    def get_filename(self, suffix: str) -> str:
        for file in self.path.iterdir():
            if file.suffix == suffix:
                return file.name
        raise FileNotFoundError(f"Artifact file with {suffix=} not found.")

    @property
    def data(self) -> pd.DataFrame:
        metadata = self.metadata
        fl_table_schema = core.reformat_oep_to_frictionless_schema(metadata["resources"][0]["schema"])
        resource = frictionless.Resource(
            name=metadata["name"],
            profile="tabular-data-resource",
            source=self.path / f"{self.filename}.csv",
            schema=fl_table_schema,
            format="csv",
        )
        return resource.to_pandas()

    def get_subprocesses(self):
        """
        Return list of subprocesses for given artifact.

        Returns entries of column "type" as list.

        Returns
        -------
        List[str]
            List of subprocesses in given artifact
        """
        return list(pd.read_csv(self.path / self.get_filename(".csv"), usecols=("type",))["type"])


def check_collection_meta(collection_meta: dict):
    """Simple checks if collection metadata is up-to-date.

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
                        "Collection metadata may changed. Please re-download collection and try again.",
                    )


def infer_collection_metadata(collection: str, collection_meta: dict) -> dict:
    """Interferes downloaded collection and updates names and subjects of artifacts in collection metadata file.

    Parameters
    ----------
    collection: str
        Name of collection
    collection_meta : dict
        Metadata of collection to be updated

    Returns
    -------
    dict
        Updated collection metadata
    """
    for group_name, artifacts in collection_meta["artifacts"].items():
        for artifact_name in artifacts:
            version = collection_meta["artifacts"][group_name][artifact_name]["latest_version"]

            artifact = Artifact(collection, group_name, artifact_name, version)
            metadata = artifact.metadata

            # Check if artifact contains multiple (sub-)processes
            try:
                type_field = [
                    field for field in metadata["resources"][0]["schema"]["fields"] if field["name"] == "type"
                ][0]
            except IndexError:
                type_field = None

            if type_field:
                collection_meta["artifacts"][group_name][artifact_name]["multiple_types"] = True
                collection_meta["artifacts"][group_name][artifact_name]["names"] = [
                    metadata["name"]
                ] + artifact.get_subprocesses()
                collection_meta["artifacts"][group_name][artifact_name]["subjects"] = [
                    ontology.get_subject(metadata)
                ] + [
                    ontology.get_name_from_annotation(value_reference)
                    for value_reference in type_field["valueReference"]
                ]
            else:
                collection_meta["artifacts"][group_name][artifact_name]["multiple_types"] = False
                collection_meta["artifacts"][group_name][artifact_name]["names"] = [metadata["name"]]
                collection_meta["artifacts"][group_name][artifact_name]["subjects"] = [ontology.get_subject(metadata)]

            collection_meta["artifacts"][group_name][artifact_name]["datatype"] = get_data_type(metadata)

    return collection_meta


def get_data_type(metadata: Union[str, pathlib.Path, dict]):
    metadata_dict: dict = core.get_metadata(metadata)
    for field in metadata_dict["resources"][0]["schema"]["fields"]:
        if field["name"].startswith("timeindex"):
            return DataType.Timeseries
    return DataType.Scalar


def get_collection_meta(collection: str) -> dict:
    """Returns collection meta file if present.

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
            f"Could not find collection meta ('{settings.COLLECTION_JSON}') "
            f"in collection folder '{collection_folder}'.",
        )
    with open(collection_meta_file, encoding="utf-8") as meta_file:
        metadata = json.load(meta_file)
    check_collection_meta(metadata)
    return metadata


def get_artifacts_from_collection(
    collection: str, process: Optional[str] = None, use_annotation: Optional[bool] = None
) -> list[Artifact]:
    """Returns list of artifacts belonging to given process (subject).

    Parameters
    ----------
    collection: str
        Collection name
    process : Optional[str]
        Name of process to search collection metadata for. If not set, all artifacts will be returned.
    use_annotation: Optional[bool]
        If set annotations are used or not used depending on value, otherwise settings value USE_ANNOTATIONS is used.

    Returns
    -------
    List[Artifact]
        List of artifacts in collection (belonging to given process, if set)
    """
    use_annotation = settings.USE_ANNOTATIONS if use_annotation is None else use_annotation
    collection_meta = get_collection_meta(collection)
    artifacts = []
    for group in collection_meta["artifacts"]:
        for artifact, artifact_info in collection_meta["artifacts"][group].items():
            process_names = artifact_info["subjects"] if use_annotation else artifact_info["names"]
            if process and process not in process_names:
                continue
            filename = artifact
            artifacts.append(
                Artifact(
                    collection,
                    group,
                    artifact,
                    artifact_info["latest_version"],
                    filename,
                    datatype=DataType(artifact_info["datatype"]),
                    multiple_types=artifact_info["multiple_types"],
                ),
            )
    return artifacts


def get_artifact_from_collection(collection: str, group: str, artifact: str, version: Optional[str] = None) -> Artifact:
    """
    Return artifact from collection.

    Parameters
    ----------
    collection: str
        Collection name
    group: str
        Group name
    artifact: str
        Artifact name
    version: Optional[str]
        Version of artifact, if not given, latest version found in collection meta is used

    Returns
    -------
    Artifact
        related artifact
    """
    collection_meta = get_collection_meta(collection)
    artifact_info = collection_meta["artifacts"][group][artifact]
    return Artifact(
        collection,
        group,
        artifact,
        version=artifact_info["latest_version"] if version is None else version,
        filename=artifact,
        datatype=DataType(artifact_info["datatype"]),
        multiple_types=artifact_info["multiple_types"],
    )


def get_processes_from_collection(collection: str) -> set[str]:
    """
    Return all (sub-)processes of a collection

    Parameters
    ----------
    collection: str
        Name of collection

    Returns
    -------
    list[str]
        List of processes
    """
    collection_meta = get_collection_meta(collection)
    processes = set()
    for artifacts in collection_meta["artifacts"].values():
        for artifact in artifacts.values():
            processes |= set(artifact["names"])
    return processes
