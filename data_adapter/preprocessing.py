"""Module to preprocess process data"""
import logging
import math
import pathlib
import warnings
from collections import ChainMap, namedtuple
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

from data_adapter import collection, core, settings
from data_adapter.structure import Structure, StructureError
from data_adapter.unit_conversion import (
    IncompatibleUnitsError,
    UnitConversionError,
    get_conversion_factor,
)

SCALAR_MERGE_GROUPS = ["region", "year"]
TIMESERIES_MERGE_GROUPS = [
    "region",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
]

ForeignKey = namedtuple("ForeignKey", ("process", "parameter"))


@dataclass
class Process:
    """Holds process data"""

    scalars: pd.DataFrame
    timeseries: pd.DataFrame
    units: dict[str, str]
    inputs: list[str] | None = None
    outputs: list[str] | None = None
    parameters: dict[str, list[str]] | None = None


class PreprocessingError(Exception):
    """Raised if preprocessing fails"""


class Adapter:
    def __init__(
        self, collection_name: str, structure: Optional[Structure] = None, units: Optional[list[str]] = None
    ) -> None:
        """The adapter is used to handle collection, structure and links centralized.

        Parameters
        ----------
        collection_name : str
            Name of collection from collection folder to get data from
        structure : Structure
            holding processes and parameters from Excel-file
        units : list[str]
            try to convert data with units in metadata into given units
        """
        self.collection_name = collection_name
        self.structure = structure
        self.units = [] if units is None else units

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
        units = {}
        for artifact in artifacts:
            df, artifact_units = self.__get_df_from_artifact(artifact, process)
            units = {**units, **artifact_units}
            if artifact.datatype == collection.DataType.Scalar:
                # Handle foreign keys (only possible in scalar data)
                foreign_keys = self._get_foreign_keys(process, df)
                for fk_column, foreign_key in foreign_keys.items():
                    artifacts = collection.get_artifacts_from_collection(
                        self.collection_name, foreign_key.process, use_annotation=False
                    )
                    if not artifacts:
                        continue  # no candidate
                    if len(artifacts) > 1:
                        raise StructureError(
                            f"Foreign key for process '{process}' points to subject '{foreign_key.process}' "
                            "which is not unique.",
                        )
                    foreign_df, foreign_units = self.__get_df_from_artifact(artifacts[0], foreign_key.process, foreign_key.parameter)
                    units[fk_column] = foreign_units[getattr(foreign_key, "parameter")]
                    foreign_df = foreign_df.rename({foreign_key.parameter: fk_column}, axis=1)
                    if artifacts[0].datatype == collection.DataType.Scalar:
                        scalar_dfs.append(foreign_df)
                    else:
                        timeseries_df.append(foreign_df)
                    # Remove FK column from original process
                    df = df.drop(fk_column, axis=1)
                scalar_dfs.append(df)
            else:
                timeseries_df.append(df)

        return Process(
            scalars=self.__merge_parameters(*scalar_dfs, datatype=collection.DataType.Scalar),
            timeseries=self.__refactor_timeseries(
                self.__merge_parameters(*timeseries_df, datatype=collection.DataType.Timeseries)
            ),
            units=units,
            inputs=self.structure.processes[process]["inputs"] if self.structure else None,
            outputs=self.structure.processes[process]["outputs"] if self.structure else None,
            parameters=self.structure.parameters[process]
            if self.structure and "process" in self.structure.parameters
            else None,
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
            if structure is not given
        """
        if self.structure is None:
            raise StructureError(
                "No structure given. "
                "You have to init adapter class with structure in order to use structure functions."
            )
        return self.structure.parameters

    def get_process_list(self) -> dict[str, dict[str, list[str]]]:
        """Return all processes from given structure, including inputs and outputs.

        Returns
        -------
        dict[str, dict[str, list[str]]]
            holding processes and related inputs and outputs

        Raises
        ------
        StructureError
            if structure name is not given
        """
        if self.structure is None:
            raise StructureError(
                "No structure given. "
                "You have to init adapter class with structure in order to use structure functions."
            )
        return self.structure.processes

    def __get_df_from_artifact(self, artifact: collection.Artifact, process: str, *parameters: str) -> (
            pd.DataFrame,
            dict
    ):
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
        df = artifact.data

        if artifact.multiple_types:
            # Fill empty types with table process name
            df["type"] = df["type"].fillna(artifact.metadata["name"])
            df = self.__filter_subprocess(df, process)
        if len(parameters) > 0:
            df = self.__filter_parameters(df, parameters, artifact.datatype)
        df, df_units = self.__convert_units(df, artifact.metadata)

        # Unpack regions:
        if artifact.datatype == collection.DataType.Scalar:
            df = df.explode("region")

        df = self.__unpack_bandwidths(df)

        return df, df_units

    def __convert_units(self, df: pd.DataFrame, metadata: dict) -> (pd.DataFrame, dict):  # noqa: C901
        """
        Converts units

        Parameters
        ----------
        df : pd.DataFrame
            Multiply columns with related conversion factor
        metadata : dict
            Find units of data in metadata

        Returns
        -------
        pd.DataFrame
            with converted units, if unit conversion is possible
        """

        def convert_series(series: list[float], factor: float) -> list[float]:
            return [item * factor for item in series]

        df_units = {}
        if df.empty:
            return df
        for field in metadata["resources"][0]["schema"]["fields"]:
            if "unit" not in field:
                continue
            if field["unit"] is None:
                continue
            if field["name"] not in df.columns:
                continue
            if isinstance(df[field["name"]].iloc[-1], str):
                continue
            df_units[field["name"]] = field["unit"]
            conversion_factor = None
            for unit in self.units:
                try:
                    conversion_factor = get_conversion_factor(field["unit"], unit)
                    df_units[field["name"]] = unit
                except (UnitConversionError, IncompatibleUnitsError):
                    continue
                break
            if conversion_factor:
                if "array" in field["type"]:
                    df[field["name"]] = df[field["name"]].apply(convert_series, factor=conversion_factor)
                else:
                    df[field["name"]] = df[field["name"]] * conversion_factor
        return df, df_units

    def __unpack_bandwidths(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes Dataframe right and unpacks all found bandwidths.

        Currently only supports to return the first argument of bandwidths
        Different bandwidth types are not supported yet

        Parameters
        ----------
        df: pd.DataFrame
            Data to unpack bandwidths

        Returns
        -------
        pd.DataFrame
            Modified Dataframe
        """
        if "bandwidth_type" not in df.columns:
            return df

        if "bandwidth_type" in df.columns:
            # Iterate rows of dataframe
            for index, row in df.iterrows():
                bandwidth_keys = row["bandwidth_type"].keys()
                for col in df.columns:
                    if col in bandwidth_keys and isinstance(row[col], list):
                        # Replace Values
                        if row[col]:
                            df.at[index, col] = row[col][0]
                        else:
                            df.at[index, col] = None
        return df

    @staticmethod
    def __filter_subprocess(df: pd.DataFrame, subprocess: str) -> pd.DataFrame:
        df = df[df["type"] == subprocess]
        df = df.dropna(axis=1, how="all")
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
        if merged_regions.empty:
            # This must be done, otherwise grouped columns appear in index and columns and cannot be reset afterwards
            merged_regions = merged_regions.drop(SCALAR_MERGE_GROUPS, axis=1)
        return merged_regions.reset_index()

    def __apply_parameter_merge(self, data, datatype):
        datamodel_columns = core.SCALAR_COLUMNS if datatype == collection.DataType.Scalar else core.TIMESERIES_COLUMNS
        groups = SCALAR_MERGE_GROUPS if datatype == collection.DataType.Scalar else TIMESERIES_MERGE_GROUPS

        series = pd.Series(dtype=object)
        for column in data.columns:
            if column in ["id", "version", *groups]:
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
                if dict_value is None or (isinstance(dict_value, float) and math.isnan(dict_value)):
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
        timeseries: dict[tuple, pd.Series] = {}
        for _, row in timeseries_raw.iterrows():
            timeindex = pd.date_range(
                start=row["timeindex_start"], end=row["timeindex_stop"], freq=pd.Timedelta(row["timeindex_resolution"])
            )
            for ts_column in ts_columns:
                ts_index = (ts_column, row["region"])
                ts_series = pd.Series(row[ts_column], index=timeindex, name=ts_index)
                if ts_index in timeseries:
                    timeseries[ts_index] = pd.concat([timeseries[ts_index], ts_series])
                else:
                    timeseries[ts_index] = ts_series
        merged_timeseries = pd.concat(timeseries.values(), axis=1)
        merged_timeseries.columns.names = ("name", "region")
        return merged_timeseries

    @staticmethod
    def _get_foreign_keys(process: str, df: pd.DataFrame) -> dict[str, ForeignKey]:
        """
        Detect and check foreign keys in scalar data and return related columns and references

        Parameters
        ----------
        process: str
            Name of process
        df
            Process data in scalar format (only scalar data holds FKs)

        Returns
        -------
        Dict of columns which hold foreign keys and related foreign key
        """
        # Column must contain string
        converted_df = df.convert_dtypes()
        string_columns = set(converted_df.dtypes[converted_df.dtypes == "string"].index)
        fk_column_candidates = string_columns - set(core.SCALAR_COLUMNS)
        logging.info(f"Possible FK candidates for {process=}: {fk_column_candidates}")

        # Check if Fks are unique (cannot have different FKs per process/subprocess)
        fk_candidates = {}
        for fk_column in fk_column_candidates:
            column_data_without_none = df[fk_column][~df[fk_column].isnull()]
            if len(column_data_without_none.unique()) > 1:
                continue  # no candidate
            fk = column_data_without_none.iloc[0]
            if "." not in fk:
                continue  # no candidate
            if df[fk_column].isnull().sum() > 0:
                logging.warning(
                    f"None values in column '{fk_column}' of process '{process}' will be overwritten by FK values."
                )
            fk_candidates[fk_column] = ForeignKey(*fk.split("."))
        return fk_candidates


def get_process(collection_name: str, process: str) -> Process:
    """Loads data for given process from collection. (Deprecated! Use Adapter class instead).

    Column headers are translated using ontology. Multiple dataframes per datatype are merged.

    Parameters
    ----------
    collection_name : str
        Name of collection to get data from
    process : str
        Name of process (from subject or metadata name, depends on USE_ANNOTATIONS)

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
    adapter = Adapter(collection_name, structure=None)
    return adapter.get_process(process)
