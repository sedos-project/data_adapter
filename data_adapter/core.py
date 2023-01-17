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

OEP_TO_FRICTIONLESS_CONVERSION = {
    "int": "integer",
    "bigint": "integer",
    "text": "string",
    "json": "object",
    "decimal": "number",
    "interval": "any",
    "timestamp": "datetime",
    "float": "number",
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


def reformat_oep_to_frictionless_schema(schema):
    # Ignore other fields than 'fields' and 'primaryKey' (i.e. "foreignKeys")
    fields = []
    for field in schema["fields"]:
        if "array" in field["type"]:
            type_ = "array"
        else:
            type_ = OEP_TO_FRICTIONLESS_CONVERSION.get(field["type"], field["type"])
        field_data = {"name": field["name"], "type": type_}
        if field["type"] == "float":
            field_data["floatNumber"] = "True"
        fields.append(field_data)
    return {"fields": fields, "primaryKey": schema["primaryKey"], "foreignkeys": []}
