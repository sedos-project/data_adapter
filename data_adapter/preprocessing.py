"""Module to preprocess process data"""
import logging
import math
import pathlib
import warnings
from collections import ChainMap
from dataclasses import dataclass
from typing import Iterable

import frictionless
import pandas as pd

from data_adapter import collection, core, settings, structure

SCALAR_MERGE_GROUPS = ["region", "year"]
TIMESERIES_MERGE_GROUPS = [
    "region",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
]


@dataclass
class Process:
    """Holds process data"""

    scalars: pd.DataFrame
    timeseries: pd.DataFrame


class PreprocessingError(Exception):
    """Raised if preprocessing fails"""


class Adapter:
    def __init__(self, collection_name: str, structure_name: str | None = None, links_name: str | None = None) -> None:
        """The adapter is used to handle collection, structure and links centralized.

        Parameters
        ----------
        collection_name : str
            Name of collection from collection folder to get data from
        structure_name : Optional[str]
            Name of structure in structure folder to read energysystem structure from
        links_name : Optional[str]
            Name of links in structure folder to read additional links for processes
        """
        self.collection_name = collection_name
        self.structure_name = structure_name
        self.links_name = links_name

    def get_process(self, process: str) -> Process:
        """Loads data for given process from collection.

        Column headers are translated using ontology. Multiple dataframes per datatype are merged.

        Parameters
        ----------
        process : str
            Name of process (from subject or metadata name, depends on USE_ANNOTATIONS)

        Returns
        -------
        Process
            Scalars and timeseries for given process. DataFrame column headers are translated by ontology.

        Raises
        ------
        FileNotFoundError
            if collection is not present in collection folder
        KeyError
            if process cannot be found in collection
        StructureError
            if additional parameters of process are related to multiple subjects
        """
        collection_folder = pathlib.Path(settings.COLLECTIONS_DIR) / self.collection_name
        if not collection_folder.exists():
            raise FileNotFoundError(
                f"Could not find {self.collection_name=} in collection folder '{settings.COLLECTIONS_DIR}'.",
            )
        artifacts = collection.get_artifacts_from_collection(self.collection_name, process)
        if not artifacts:
            raise KeyError(f"Could not find {process=} in collection '{self.collection_name}'.")

        # Get dataframes from processes by subject
        scalar_dfs = []
        timeseries_df = []
        for artifact in artifacts:
            df = self.__get_df_from_artifact(artifact, process)
            if artifact.datatype == collection.DataType.Scalar:
                scalar_dfs.append(df)
            else:
                timeseries_df.append(df)

        # Get dataframes for processes from additional parameters
        if self.links_name:
            for subject, parameters in structure.get_links_for_process(process, links_name=self.links_name).items():
                artifacts = collection.get_artifacts_from_collection(self.collection_name, subject)
                if not artifacts:
                    raise structure.StructureError(f"Could not find linked parameter for {process=} and {subject=}.")
                if len(artifacts) > 1:
                    raise structure.StructureError(
                        f"Linked parameter for process '{process}' points to subject '{subject}' which is not unique.",
                    )
                df = self.__get_df_from_artifact(artifacts[0], subject, *parameters)
                if artifacts[0].datatype == collection.DataType.Scalar:
                    scalar_dfs.append(df)
                else:
                    timeseries_df.append(df)

        return Process(
            self.__merge_parameters(*scalar_dfs, datatype=collection.DataType.Scalar),
            self.__refactor_timeseries(
                self.__merge_parameters(*timeseries_df, datatype=collection.DataType.Timeseries)
            ),
        )

    def get_structure(self) -> dict:
        """Return energy structure for structure name of adapter.

        Returns
        -------
        dict
            containing energy structure

        Raises
        ------
        StructureError
            if structure name is not given
        """
        if self.structure_name:
            return structure.get_energy_structure(self.structure_name)
        else:
            raise structure.StructureError(
                "No structure name given. "
                "You have to init adapter class with structure name in order to use structure functions.",
            )

    def get_process_list(self) -> list[str]:
        """Return all processes from given structure.

        Returns
        -------
        List[str]
            List of processes

        Raises
        ------
        StructureError
            if structure name is not given
        """
        if self.structure_name:
            return structure.get_processes(self.structure_name)
        else:
            raise structure.StructureError(
                "No structure name given. "
                "You have to init adapter class with structure name in order to use structure functions.",
            )

    def __get_df_from_artifact(self, artifact: collection.Artifact, process: str, *parameters: str) -> pd.DataFrame:
        """Returns DataFrame from given artifact.

        If parameters are given, artifact columns are filtered for given parameters
        and default columns from datatype.

        Parameters
        ----------
        artifact: Artifact
            Artifact to get DataFrame from
        process: str
            Process to filter (needed in case of multiple subprocesses)
        parameters: tuple[str]
            Parameters to filter DataFrame

        Returns
        -------
        pd.DataFrame
        """
        metadata = artifact.metadata
        fl_table_schema = core.reformat_oep_to_frictionless_schema(metadata["resources"][0]["schema"])
        resource = frictionless.Resource(
            name=metadata["name"],
            profile="tabular-data-resource",
            source=artifact.path / f"{artifact.filename}.csv",
            schema=fl_table_schema,
            format="csv",
        )
        df = resource.to_pandas()

        if artifact.multiple_types:
            df = self.__filter_subprocess(df, process)
        if len(parameters) > 0:
            df = self.__filter_parameters(df, parameters, artifact.datatype)

        # Unpack regions:
        if artifact.datatype == collection.DataType.Scalar:
            return df.explode("region")
        return df

    @staticmethod
    def __filter_subprocess(df: pd.DataFrame, subprocess: str) -> pd.DataFrame:
        df = df[df["type"] == subprocess]
        return df.drop("type", axis=1)

    @staticmethod
    def __filter_parameters(
        df: pd.DataFrame,
        parameters: Iterable[str],
        datatype: collection.DataType,
    ) -> pd.DataFrame:
        """Filters dataframe columns by parameter list.

        Parameters
        ----------
        df: pd.DataFrame
            Data to filter columns from
        parameters: Iterable[str]
            Tuple of parameters to filter columns
        datatype: collection.DataType
            Type of dataframe (scalar or timeseries)

        Returns
        -------
        pd.DataFrame
            Filtered data frame with remaining columns from parameter list
        """
        columns = set(core.SCALAR_COLUMNS) if datatype is collection.DataType.Scalar else set(core.TIMESERIES_COLUMNS)
        columns.update(set(parameters))
        drop_columns = set(df.columns).difference(columns)
        return df.drop(drop_columns, axis=1)

    def __merge_parameters(self, *df: pd.DataFrame, datatype: collection.DataType) -> pd.DataFrame:
        """Merges parameters.

        Parameters
        ----------
        df: pd.DataFrame
            Data holding list of strings as regions
        datatype: collection.DataType
            Scalar or timeseries

        Returns
        -------
        pd.DataFrame
            Each region in the dataframe has its own row
        """
        if len(df) == 0:
            return pd.DataFrame(dtype=object)
        concatenated_dfs = pd.concat(df)
        concatenated_dfs["region"] = concatenated_dfs["region"].apply(lambda x: tuple(x) if isinstance(x, list) else x)
        groups = SCALAR_MERGE_GROUPS if datatype == collection.DataType.Scalar else TIMESERIES_MERGE_GROUPS
        merged_regions = concatenated_dfs.groupby(groups).apply(self.__apply_parameter_merge, datatype=datatype)
        return merged_regions.reset_index()

    def __apply_parameter_merge(self, data, datatype):
        datamodel_columns = core.SCALAR_COLUMNS if datatype == collection.DataType.Scalar else core.TIMESERIES_COLUMNS
        groups = SCALAR_MERGE_GROUPS if datatype == collection.DataType.Scalar else TIMESERIES_MERGE_GROUPS

        series = pd.Series(dtype=object)
        for column in data.columns:
            if column in ["id", *groups]:
                continue  # Drop columns
            try:
                series[column] = self.__merge_column(column, data[column], datamodel_columns)
            except ValueError:
                region = data["region"].iloc[0]
                raise PreprocessingError(f"Merging of {region=} failed, due to duplicate value entries.")
        return series

    @staticmethod
    def __merge_column(column, values, datamodel_columns):
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
                raise PreprocessingError(f"Multiple values defined for {column=}: ({v}, {value})")
            value = v
        return value

    @staticmethod
    def __refactor_timeseries(timeseries_raw: pd.DataFrame) -> pd.DataFrame:
        """Takes timeseries in single line parameter-model format (start, end, freq,
        region, ts-array...) and turns into Tabular matching format with timeindex
        as timeseries timestamps, technology-region as header and columns
        containing data.

        Parameters
        ----------
        timeseries_raw : pd.Dataframe
            Raw timeseries containing columns with start, end and resolution of timeseries and array
            containing related data.

        Returns
        -------
        pd.DataFrame:
            Tabular form of timeseries for multiple periods of similar
            technologies and regions.
        """
        if timeseries_raw.empty:
            return timeseries_raw
        ts_columns = set(timeseries_raw.columns).difference(core.TIMESERIES_COLUMNS.keys())
        timeseries = []
        for _, row in timeseries_raw.iterrows():
            timeindex = pd.date_range(
                start=row["timeindex_start"], end=row["timeindex_stop"], freq=pd.Timedelta(row["timeindex_resolution"])
            )
            for ts_column in ts_columns:
                timeseries.append(pd.Series(row[ts_column], index=timeindex, name=(ts_column, row["region"])))
        merged_timeseries = pd.concat(timeseries, axis=1)
        merged_timeseries.columns.names = ("name", "region")
        return merged_timeseries


def get_process(collection_name: str, process: str, links: str) -> Process:
    """Loads data for given process from collection. (Deprecated! Use Adapter class instead).

    Column headers are translated using ontology. Multiple dataframes per datatype are merged.

    Parameters
    ----------
    collection_name : str
        Name of collection to get data from
    process : str
        Name of process (from subject or metadata name, depends on USE_ANNOTATIONS)
    links : str
        Name of file to get linked parameters from

    Returns
    -------
    Process
        Scalars and timeseries for given process. DataFrame column headers are translated by ontology.
    """
    deprecated_msg = (
        "`preprocessing.get_process` function is deprecated. "
        "Instead, initialize `Adapter` class and get process from there."
    )
    logging.warning(deprecated_msg)
    warnings.warn(deprecated_msg, DeprecationWarning)
    adapter = Adapter(collection_name, structure_name=None, links_name=links)
    return adapter.get_process(process)
