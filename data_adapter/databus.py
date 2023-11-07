import json
import logging
import os
import pathlib
import re
from typing import Union

import requests
from SPARQLWrapper import JSON, SPARQLWrapper2

from data_adapter import collection, settings


def download_artifact(artifact_file: str, filename: Union[pathlib.Path, str]):
    """Downloads an artifact file and stores it under given filename.

    Parameters
    ----------
    artifact_file: str
        URI to artifact file
    filename: str
        Path to store downloaded file

    Raises
    ------
    FileNotFoundError
        if request fails
    """
    response = requests.get(artifact_file, timeout=90)
    if response.status_code != 200:
        raise FileNotFoundError(f"Could not find artifact file '{artifact_file}'")
    with open(os.path.join(filename), "wb") as f:
        # Replace single quotes with two double quotes to enable arrays and JSON/dicts in CSV cells:
        f.write(re.sub(b"'", b'""', response.content))


def get_artifact_filenames(artifact: str, version: str) -> list[str]:
    sparql = SPARQLWrapper2(settings.DATABUS_ENDPOINT)
    sparql.setReturnFormat(JSON)

    sparql.setQuery(
        f"""
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcat:   <http://www.w3.org/ns/dcat#>
        PREFIX dct:    <http://purl.org/dc/terms/>
        PREFIX dcv:    <https://dataid.dbpedia.org/databus-cv#>
        PREFIX dataid: <https://dataid.dbpedia.org/databus#>
        SELECT ?file WHERE
        {{
            GRAPH ?g
            {{
                ?dataset dataid:artifact <{artifact}> .
                ?distribution <http://purl.org/dc/terms/hasVersion> '{version}' .
                ?distribution dataid:file ?file .
            }}
        }}
        """,
    )
    result = sparql.query()
    return [file["file"].value for file in result.bindings]


def get_latest_version_of_artifact(artifact: str) -> str:
    """Returns the latest version of given artifact.

    Parameters
    ----------
    artifact: str
        DataId of artifact to check version of

    Returns
    -------
    str
        Latest version of given artifact
    """
    sparql = SPARQLWrapper2(settings.DATABUS_ENDPOINT)
    sparql.setReturnFormat(JSON)

    sparql.setQuery(
        f"""
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcat:   <http://www.w3.org/ns/dcat#>
        PREFIX dct:    <http://purl.org/dc/terms/>
        PREFIX dcv:    <https://dataid.dbpedia.org/databus-cv#>
        PREFIX dataid: <https://dataid.dbpedia.org/databus#>
        SELECT ?version WHERE
        {{
            GRAPH ?g
            {{
                ?dataset dataid:artifact <{artifact}> .
                ?dataset dct:hasVersion ?version .
            }}
        }} ORDER BY DESC (?version) LIMIT 1
        """,
    )
    result = sparql.query()
    return result.bindings[0]["version"].value


def get_artifacts_from_collection(collection: str) -> list[str]:
    """Returns list of all artifacts found in given collection.

    Parameters
    ----------
    collection: str
        URL to databus collection

    Returns
    -------
    List[str]
        List of artifacts in collection
    """

    def extract_artifact_from_uri(uri: str):
        https, _, host, user, group, artifact, version, name = uri.split("/")
        return "/".join((https, _, host, user, group, artifact))

    response = requests.get(collection, headers={"Accept": "text/sparql"}, timeout=90)
    sparql = SPARQLWrapper2(settings.DATABUS_ENDPOINT)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(response.text)
    data = sparql.query()
    files = {extract_artifact_from_uri(file["file"].value) for file in data.bindings}
    return list(files)


def download_collection(collection_url: str, force_download=False):
    """Downloads all artifact files for given collection and saves it to local output directory.

    Parameters
    ----------
    collection_url : str
        URL of collection on databus
    force_download : bool
        Downloads the latest versions, even if version is already present

    Raises
    ------
    CollectionError
        If version of collection metadata differs
    """
    logging.info(f"Downloading collection from URL '{collection_url}'...")
    collection_name = collection_url.rstrip("/").split("/")[-1]
    collection_dir = settings.COLLECTIONS_DIR / collection_name
    collection_meta = {"name": collection_url, "version": settings.COLLECTION_META_VERSION, "artifacts": {}}
    if collection_dir.exists():
        if (collection_dir / settings.COLLECTION_JSON).exists():
            with open(collection_dir / settings.COLLECTION_JSON, encoding="utf-8") as collection_json_file:
                collection_meta = json.load(collection_json_file)
    else:
        collection_dir.mkdir()

    if collection_meta.get("version", None) != settings.COLLECTION_META_VERSION:
        raise collection.CollectionError(
            "Collection metadata has changed. Please remove collection and re-download. "
            "Otherwise, strange behaviours could occur.",
        )

    artifacts = get_artifacts_from_collection(collection_url)
    artifact_versions = {artifact: get_latest_version_of_artifact(artifact) for artifact in artifacts}
    __download_artifacts(artifact_versions, collection_dir, collection_meta, force_download)
    collection_meta = collection.infer_collection_metadata(collection_name, collection_meta)

    with open(collection_dir / settings.COLLECTION_JSON, "w", encoding="utf-8") as collection_json_file:
        json.dump(collection_meta, collection_json_file)


def __download_artifacts(
    artifact_versions: dict,
    collection_dir: pathlib.Path,
    collection_meta: dict,
    force_download: bool,
):
    """Download artifacts from collection.

    Downloads artifacts into collection folder and updates/creates collection metadata.

    Parameters
    ----------
    artifact_versions: dict
        Dictionary containing artifact names (key) and latest version (value)
    collection_dir: pathlib.Path
        Folder to download artifacts
    collection_meta: dict
        Metadata of collection. Gets updated with artifact infos.
    force_download: bool
        Whether to download artifact, independent of version.
    """
    for artifact, version in artifact_versions.items():
        group_name = artifact.split("/")[-2]
        if group_name not in collection_meta["artifacts"]:
            collection_meta["artifacts"][group_name] = {}
        artifact_name = artifact.split("/")[-1]
        if artifact_name not in collection_meta["artifacts"][group_name]:
            collection_meta["artifacts"][group_name][artifact_name] = {}

        latest_version = collection_meta["artifacts"][group_name][artifact_name].get("latest_version")
        if not force_download and latest_version and latest_version == version:
            logging.info(f"Skipping download of {artifact_name=} {version=} as latest version is already present.")
            continue
        collection_meta["artifacts"][group_name][artifact_name]["latest_version"] = version

        group_dir = collection_dir / group_name
        if not group_dir.exists():
            group_dir.mkdir()
        artifact_dir = group_dir / artifact_name
        if not artifact_dir.exists():
            artifact_dir.mkdir()

        version_dir = artifact_dir / version
        if not version_dir.exists():
            version_dir.mkdir()

        artifact_filenames = get_artifact_filenames(artifact, version)
        for artifact_filename in artifact_filenames:
            suffix = artifact_filename.split(".")[-1]
            filename = f"{artifact_name}.{suffix}"
            download_artifact(artifact_filename, version_dir / filename)
        logging.info(f"Downloaded {artifact_name=} {version=}.")
