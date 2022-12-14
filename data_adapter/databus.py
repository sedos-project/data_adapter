import json
import logging
import os
import pathlib
import urllib.parse
from typing import List, Union

import requests
from SPARQLWrapper import JSON, SPARQLWrapper2

from data_adapter import core, ontology, settings


def download_artifact(artifact_file: str, filename: Union[pathlib.Path, str]):
    """
    Downloads an artifact file and stores it under given filename

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
        f.write(response.content)


def get_artifact_filenames(artifact: str, version: str) -> List[str]:
    sparql = SPARQLWrapper2(settings.DATABUS_ENDPOINT)
    sparql.setReturnFormat(JSON)

    sparql.setQuery(
        f"""
        PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcat:   <http://www.w3.org/ns/dcat#>
        PREFIX dct:    <http://purl.org/dc/terms/>
        PREFIX dcv: <http://dataid.dbpedia.org/ns/cv#>
        PREFIX dataid: <http://dataid.dbpedia.org/ns/core#>
        SELECT ?file WHERE
        {{
            GRAPH ?g
            {{
                ?dataset dataid:artifact <{artifact}> .
                ?distribution <http://purl.org/dc/terms/hasVersion> '{version}' .
                ?distribution dataid:file ?file .
            }}
        }}
        """
    )
    result = sparql.query()
    return [file["file"].value for file in result.bindings]


def get_latest_version_of_artifact(artifact: str) -> str:
    """
    Returns the latest version of given artifact

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
        PREFIX dcv: <http://dataid.dbpedia.org/ns/cv#>
        PREFIX dataid: <http://dataid.dbpedia.org/ns/core#>
        SELECT ?version WHERE
        {{
            GRAPH ?g
            {{
                ?dataset dataid:artifact <{artifact}> .
                ?dataset dct:hasVersion ?version .
            }}
        }} ORDER BY DESC (?version) LIMIT 1
        """
    )
    result = sparql.query()
    return result.bindings[0]["version"].value


def get_artifacts_from_collection(collection: str) -> List[str]:
    """
    Returns list of all artifacts found in given collection

    Parameters
    ----------
    collection: str
        URL to databus collection

    Returns
    -------
    List[str]
        List of artifacts in collection
    """

    def find_artifact(node):
        if len(node["childNodes"]) == 0:
            yield node["uri"]
        for child in node["childNodes"]:
            yield from find_artifact(child)

    response = requests.get(
        collection, headers={"Content-Type": "text/sparql"}, timeout=90
    )
    data = response.json()
    content_raw = urllib.parse.unquote(data["@graph"][0]["content"])
    content = json.loads(content_raw)
    return list(find_artifact(content["root"]))


def download_collection(collection_url: str, force_download=False):
    """
    Downloads all artifact files for given collection and saves it to local output directory

    Parameters
    ----------
    collection_url : str
        URL of collection on databus
    force_download : bool
        Downloads the latest versions, even if version is already present
    """
    collection_name = collection_url.rstrip("/").split("/")[-1]
    collection_dir = settings.COLLECTIONS_DIR / collection_name
    collection_meta = {}
    if collection_dir.exists():
        if (collection_dir / settings.COLLECTION_JSON).exists():
            with open(
                collection_dir / settings.COLLECTION_JSON, "r", encoding="utf-8"
            ) as collection_json_file:
                collection_meta = json.load(collection_json_file)
    else:
        collection_dir.mkdir()

    artifacts = get_artifacts_from_collection(collection_url)
    artifact_versions = {
        artifact: get_latest_version_of_artifact(artifact) for artifact in artifacts
    }
    for artifact, version in artifact_versions.items():
        group_name = artifact.split("/")[-2]
        if group_name not in collection_meta:
            collection_meta[group_name] = {}
        artifact_name = artifact.split("/")[-1]
        if artifact_name not in collection_meta[group_name]:
            collection_meta[group_name][artifact_name] = {}

        latest_version = collection_meta[group_name][artifact_name].get(
            "latest_version"
        )
        if not force_download and latest_version and latest_version == version:
            logging.info(
                f"Skipping download of {artifact_name=} {version=} as latest version is already present."
            )
            continue
        collection_meta[group_name][artifact_name]["latest_version"] = version

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
            if suffix == "json":
                metadata = core.get_metadata(version_dir / filename)
                collection_meta[group_name][artifact_name][
                    "subject"
                ] = ontology.get_subject(metadata)
                collection_meta[group_name][artifact_name][
                    "datatype"
                ] = core.get_data_type(metadata)
        logging.info(f"Downloaded {artifact_name=} {version=}.")

    with open(
        collection_dir / settings.COLLECTION_JSON, "w", encoding="utf-8"
    ) as collection_json_file:
        json.dump(collection_meta, collection_json_file)
