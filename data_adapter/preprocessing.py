import json
import pathlib
from dataclasses import dataclass
from typing import Dict, List

import frictionless
import pandas

from data_adapter import core, settings, structure


class CollectionError(Exception):
    """Raised if collection data or metadata is invalid"""


@dataclass
class Artifact:
    collection: str
    group: str
    artifact: str
    version: str
    filename: str
    subject: str
    datatype: core.DataType

    def path(self):
        return (
            settings.COLLECTIONS_DIR
            / self.collection
            / self.group
            / self.artifact
            / self.version
        )


def __get_collection_meta(collection: str) -> dict:
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
    __check_collection_meta(metadata)
    return metadata


def __check_collection_meta(collection_meta: dict):
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
    # Check if artifact info keys are missing:
    for group, artifacts in collection_meta.items():
        for artifact, artifact_infos in artifacts.items():
            for key in ("latest_version", "subject", "datatype"):
                if key not in artifact_infos:
                    raise CollectionError(
                        f"Collection metadata is invalid ({group=}, {artifact=} misses {key=}). "
                        "Collection metadata may changed. Please re-download collection and try again."
                    )


def __get_artifacts_for_process(collection: str, process: str) -> List[Artifact]:
    """
    Returns list of artifacts belonging to given process (subject)

    Parameters
    ----------
    collection: str
        Collection name
    process : str
        Name of process to search collection metadata for

    Returns
    -------
    List[ArtifactPath]
        List of artifacts in collection belonging to given process
    """
    collection_meta = __get_collection_meta(collection)
    artifacts = []
    for group in collection_meta:
        for artifact, artifact_info in collection_meta[group].items():
            if artifact_info["subject"] == process:
                filename = artifact
                artifacts.append(
                    Artifact(
                        collection,
                        group,
                        artifact,
                        artifact_info["latest_version"],
                        filename,
                        subject=process,
                        datatype=core.DataType(artifact_info["datatype"]),
                    )
                )
    return artifacts


def __get_df_from_artifact(artifact: Artifact, *parameters: List[str]):
    """
    Returns DataFrame from given artifact.

    If parameters are given, artifact columns are filtered for given parameters
    and default columns from datatype.

    Parameters
    ----------
    artifact: Artifact
        Artifact to get DataFrame from
    parameters: List[str]
        Parameters to filter DataFrame

    Returns
    -------
    pandas.DataFrame
    """
    with open(
        artifact.path() / f"{artifact.filename}.json", "r", encoding="utf-8"
    ) as metadata_file:
        metadata = json.load(metadata_file)
    fl_table_schema = core.reformat_oep_to_frictionless_schema(
        metadata["resources"][0]["schema"]
    )
    resource = frictionless.Resource(
        name=metadata["name"],
        profile="tabular-data-resource",
        source=artifact.path() / f"{artifact.filename}.csv",
        schema=fl_table_schema,
        format="csv",
    )
    df = resource.to_pandas()
    if len(parameters) == 0:
        return df
    columns = (
        set(core.SCALAR_COLUMNS)
        if artifact.datatype is core.DataType.Scalar
        else set(core.TIMESERIES_COLUMNS)
    )
    columns.update(set(parameters))
    drop_columns = set(df.columns).difference(columns)
    return df.drop(drop_columns, axis=1)


def get_process_df(collection: str, process: str) -> Dict[str, pandas.DataFrame]:
    """
    Loads data for given process from collection as pandas.DataFrame

    Column headers are translated using ontology.

    Parameters
    ----------
    collection : str
        Name of collection to get data from
    process : str
        Name of process (from subject)

    Returns
    -------
    Dict[str, pandas.DataFrame]
        Data for given process, keys represent related artifact. DataFrame column headers are translated by ontology.

    Raises
    ------
    FileNotFoundError
        if collection is not present in collection folder
    StructureError
        if additional parameters of process are related to multiple subjects
    """
    collection_folder = pathlib.Path(settings.COLLECTIONS_DIR) / collection
    if not collection_folder.exists():
        raise FileNotFoundError(
            f"Could not find {collection=} in collection folder '{collection_folder}'."
        )
    artifacts = __get_artifacts_for_process(collection, process)
    data = {}
    for artifact in artifacts:
        data[artifact.artifact] = __get_df_from_artifact(artifact)
    for subject, parameters in structure.get_additional_parameters(process).items():
        artifacts = __get_artifacts_for_process(collection, subject)
        if len(artifacts) > 1:
            raise structure.StructureError(
                f"Additional parameter for process '{process}' "
                f"points to subject '{subject}' which is not unique."
            )
        data[artifacts[0].artifact] = __get_df_from_artifact(artifacts[0], *parameters)
    return data
