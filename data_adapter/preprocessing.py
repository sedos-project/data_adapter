import pathlib

import frictionless
import pandas

from data_adapter import collection, core, settings, structure


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
    if len(parameters) == 0:
        return df
    return _filter_parameters(df, parameters, artifact.datatype)


def _filter_parameters(
    df: pandas.DataFrame, parameters: tuple[str], datatype: collection.DataType
) -> pandas.DataFrame:
    """
    Filters dataframe columns by parameter list.

    Parameters
    ----------
    df: pandas.DataFrame
        Data to filter columns from
    parameters: tuple[str]
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
