import json
import pathlib
from enum import IntEnum
from typing import Union

SCALAR_COLUMNS = {
    "id",
    "region",
    "year",
    "bandwidth_type",
    "version",
    "method",
    "source",
    "comment",
}
TIMESERIES_COLUMNS = {
    "id",
    "region",
    "version",
    "method",
    "source",
    "comment",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
}


class DataType(IntEnum):
    Scalar = 0
    Timeseries = 1


def get_metadata(metadata: Union[str, pathlib.Path, dict]):
    if isinstance(metadata, dict):
        return metadata
    with open(metadata, "r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def get_data_type(metadata: Union[str, pathlib.Path, dict]):
    metadata = get_metadata(metadata)
    for field in metadata["resources"][0]["schema"]["fields"]:
        if field["name"].startswith("timeindex"):
            return DataType.Timeseries
    return DataType.Scalar
