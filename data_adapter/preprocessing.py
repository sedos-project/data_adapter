import json
import pathlib
from collections import namedtuple
from typing import Dict, List, Optional, Union

import pandas

from data_adapter import settings

ArtifactPath = namedtuple("Artifact", ["group", "artifact", "version", "filename"])


def __get_collection_meta(collection_dir: pathlib.Path) -> dict:
    """
    Returns collection meta file if present

    Parameters
    ----------
    collection_dir : pathlib.Path
        Collection folder to search for collection meta

    Returns
    -------
    dict
        Metadata for given collection

    Raises
    ------
    FileNotFoundError
        if collection metadata cannot be found in given collection folder
    """
    collection_meta_file = collection_dir / settings.COLLECTION_JSON
    if not collection_meta_file.exists():
        raise FileNotFoundError(
            f"Could not find collection meta ('{settings.COLLECTION_JSON}') in collection folder '{collection_dir}'."
        )
    with open(collection_meta_file, "r", encoding="utf-8") as meta_file:
        return json.load(meta_file)


def __get_artifacts_for_process(
    collection_meta: dict, process: str
) -> List[ArtifactPath]:
    """
    Returns list of artifacts belonging to given process (subject)

    Parameters
    ----------
    collection_meta: dict
        Collection metadata
    process : str
        Name of process to search collection metadata for

    Returns
    -------
    List[ArtifactPath]
        List of artifacts in collection belonging to given process
    """
    artifacts = []
    for group in collection_meta:
        for artifact, artifact_info in collection_meta[group].items():
            if artifact_info["subject"] == process:
                filename = f"{artifact}.csv"
                artifacts.append(
                    ArtifactPath(
                        group, artifact, artifact_info["latest_version"], filename
                    )
                )
    return artifacts


def get_process_df(
    collection: str,
    process: str,
    collection_dir: Optional[Union[str, pathlib.Path]] = settings.COLLECTIONS_DIR,
) -> Dict[str, pandas.DataFrame]:
    """
    Loads data for given process from collection as pandas.DataFrame

    Column headers are translated using ontology.

    Parameters
    ----------
    collection : str
        Name of collection to get data from
    process : str
        Name of process (from subject)
    collection_dir : Optional[Union[str, pathlib.Path]]
        Folder where collections are stored, defaults to working_dir/collections

    Returns
    -------
    pandas.DataFrame
        Data for given process with column headers translated by ontology

    Raises
    ------
    FileNotFoundError
        if collection is not present in collection folder
    """
    collection_folder = pathlib.Path(collection_dir) / collection
    if not collection_folder.exists():
        raise FileNotFoundError(
            f"Could not find {collection=} in collection folder '{collection_folder}'."
        )
    collection_meta = __get_collection_meta(collection_folder)
    artifacts = __get_artifacts_for_process(collection_meta, process)
    data = {}
    for artifact in artifacts:
        artifact_path = (
            collection_folder
            / artifact.group
            / artifact.artifact
            / artifact.version
            / artifact.filename
        )
        data[artifact.artifact] = pandas.read_csv(artifact_path)
    return data
