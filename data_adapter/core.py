import datetime
import json
import pathlib
from typing import Union

SCALAR_COLUMNS = {
    "id": int,
    "region": list,
    "year": int,
    "bandwidth_type": dict,
    "version": str,
    "method": dict,
    "source": dict,
    "comment": dict,
}
TIMESERIES_COLUMNS = {
    "id": int,
    "region": list,
    "version": str,
    "method": dict,
    "source": dict,
    "comment": dict,
    "timeindex_start": datetime.datetime,
    "timeindex_stop": datetime.datetime,
    "timeindex_resolution": str,
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


def get_metadata(metadata: Union[str, pathlib.Path, dict]):
    if isinstance(metadata, dict):
        return metadata
    with open(metadata, encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


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
