import math
import pathlib
from collections import ChainMap
from typing import Iterable

import frictionless
import pandas

from data_adapter import collection, core, settings, structure

SCALAR_MERGE_GROUPS = ["region", "year"]
TIMESERIES_MERGE_GROUPS = [
    "region",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
]


class PreprocessingError(Exception):
    """Raised if"""


def __get_df_from_artifact(artifact: collection.Artifact, *parameters: str):
    """
    Returns DataFrame from given artifact.

    If parameters are given, artifact columns are filtered for given parameters
    and default columns from datatype.

    Parameters
    ----------
    artifact: Artifact
        Artifact to get DataFrame from
    parameters: tuple[str]
        Parameters to filter DataFrame

    Returns
    -------
    pandas.DataFrame

    Raises
    ------
    PreprocessingError
        if error occurs while extracting dataframe from artifact
    """
    metadata = collection.get_metadata_from_artifact(artifact)
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
    if len(parameters) > 0:
        df = _filter_parameters(df, parameters, artifact.datatype)
    try:
        return _merge_regions(df, datatype=artifact.datatype)
    except PreprocessingError:
        raise PreprocessingError(f"Error while merging regions in {artifact=}.")


def _filter_parameters(
    df: pandas.DataFrame, parameters: Iterable[str], datatype: collection.DataType
) -> pandas.DataFrame:
    """
    Filters dataframe columns by parameter list.

    Parameters
    ----------
    df: pandas.DataFrame
        Data to filter columns from
    parameters: Iterable[str]
        Tuple of parameters to filter columns
    datatype: collection.DataType
        Type of dataframe (scalar or timeseries)

    Returns
    -------
    pandas.DataFrame
        Filtered data frame with remaining columns from parameter list
    """
    columns = (
        set(core.SCALAR_COLUMNS)
        if datatype is collection.DataType.Scalar
        else set(core.TIMESERIES_COLUMNS)
    )
    columns.update(set(parameters))
    drop_columns = set(df.columns).difference(columns)
    return df.drop(drop_columns, axis=1)


def _merge_regions(
    df: pandas.DataFrame, datatype: collection.DataType
) -> pandas.DataFrame:
    """
    Unpacks region lists and merges parameters into single regions.

    Parameters
    ----------
    df: pandas.DataFrame
        Data holding list of strings as regions
    datatype: collection.DataType
        Scalar or timeseries

    Returns
    -------
    pandas.DataFrame
        Each region in the dataframe has its own row
    """
    # Unpack regions
    unpacked_regions = df.explode("region")
    groups = (
        SCALAR_MERGE_GROUPS
        if datatype == collection.DataType.Scalar
        else TIMESERIES_MERGE_GROUPS
    )
    merged_regions = unpacked_regions.groupby(groups).apply(
        _apply_region_merge, datatype=datatype
    )
    return merged_regions.reset_index()


def _apply_region_merge(data, datatype):
    datamodel_columns = (
        core.SCALAR_COLUMNS
        if datatype == collection.DataType.Scalar
        else core.TIMESERIES_COLUMNS
    )
    groups = (
        SCALAR_MERGE_GROUPS
        if datatype == collection.DataType.Scalar
        else TIMESERIES_MERGE_GROUPS
    )

    series = pandas.Series()
    for column in data.columns:
        if column in ["id"] + groups:
            continue  # Drop columns
        try:
            series[column] = merge_column(column, data[column], datamodel_columns)
        except ValueError:
            region = data["region"].iloc[0]
            raise PreprocessingError(
                f"Merging of {region=} failed, due to duplicate value entries."
            )
    return series


def merge_column(column, values, datamodel_columns):
    if column in datamodel_columns and datamodel_columns[column] is dict:
        dicts = []
        for dict_value in values:
            if dict_value is None:
                continue
            if isinstance(dict_value, dict):
                dicts.append(dict_value)
                continue
            raise PreprocessingError(f"Value in {column=} is not a dict/JSON.")
        return dict(ChainMap(*dicts))
    value = None
    for v in values:
        if v is None or (isinstance(v, (float, int)) and math.isnan(v)):
            continue
        if v and value and v != value:
            raise PreprocessingError(
                f"Multiple values defined for {column=}: ({v}, {value})"
            )
        value = v
    return value


def get_process_df(collection_name: str, process: str) -> dict[str, pandas.DataFrame]:
    """
    Loads data for given process from collection as pandas.DataFrame

    Column headers are translated using ontology.

    Parameters
    ----------
    collection_name : str
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
    collection_folder = pathlib.Path(settings.COLLECTIONS_DIR) / collection_name
    if not collection_folder.exists():
        raise FileNotFoundError(
            f"Could not find {collection_name=} in collection folder '{collection_folder}'."
        )
    artifacts = collection.get_artifacts_from_collection(collection_name, process)
    data = {}
    for artifact in artifacts:
        data[artifact.artifact] = __get_df_from_artifact(artifact)
    for subject, parameters in structure.get_additional_parameters(process).items():
        artifacts = collection.get_artifacts_from_collection(collection_name, subject)
        if len(artifacts) > 1:
            raise structure.StructureError(
                f"Additional parameter for process '{process}' "
                f"points to subject '{subject}' which is not unique."
            )
        data[artifacts[0].artifact] = __get_df_from_artifact(artifacts[0], *parameters)
    return data
