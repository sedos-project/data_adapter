import json
import os
import pathlib
import urllib.parse
from typing import List, Optional, Union

import requests
from SPARQLWrapper import JSON, SPARQLWrapper2

from data_adapter import settings


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


def download_collection(
    collection_url: str,
    collection_output_directory: Optional[
        Union[str, pathlib.Path]
    ] = settings.COLLECTIONS_DIR,
):
    """
    Downloads all artifact files for given collection and saves it to local output directory

    Parameters
    ----------
    collection_url : str
        URL of collection on databus
    collection_output_directory : Union[str, pathlib.Path]
        Path where collection is saved to
    """
    output_dir = pathlib.Path(collection_output_directory)

    collection_name = collection_url.split("/")[-1]
    collection_dir = output_dir / collection_name
    if not collection_dir.exists():
        collection_dir.mkdir()

    artifacts = get_artifacts_from_collection(collection_url)
    artifact_versions = {
        artifact: get_latest_version_of_artifact(artifact) for artifact in artifacts
    }
    for artifact, version in artifact_versions.items():
        artifact_name = artifact.split("/")[-1]
        group_name = artifact.split("/")[-2]
        group_dir = collection_dir / group_name
        if not group_dir.exists():
            group_dir.mkdir()
        artifact_filenames = get_artifact_filenames(artifact, version)
        for artifact_filename in artifact_filenames:
            suffix = artifact_filename.split(".")[-1]
            filename = f"{artifact_name}.{suffix}"
            download_artifact(artifact_filename, group_dir / filename)
