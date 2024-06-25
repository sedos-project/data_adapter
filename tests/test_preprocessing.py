import logging

import pandas
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from data_adapter import collection, core, preprocessing
from tests import utils

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def test_process():
    artifacts = preprocessing.get_process("simple", "modex_tech_storage_battery")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 16
    assert len(artifacts.scalars) == 51


def test_process_of_artifact_with_multiple_subprocesses():
    adapter = preprocessing.Adapter("subprocesses")
    onshore = adapter.get_process("wind_onshore")
    offshore = adapter.get_process("wind_offshore")

    assert hasattr(onshore, "scalars")
    assert hasattr(onshore, "timeseries")
    assert len(onshore.scalars.columns) == 12
    assert len(onshore.scalars) == 50
    assert onshore.timeseries["wind_speed", ("HE",)][0] == 1003

    assert hasattr(offshore, "scalars")
    assert hasattr(offshore, "timeseries")
    assert len(offshore.scalars.columns) == 12
    assert len(offshore.scalars) == 50
    assert offshore.timeseries["wind_speed", ("HE",)][0] == 10003


def test_process_with_annotations():
    with utils.turn_on_annotations():
        artifacts = preprocessing.get_process("simple", "battery storage")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 16
    assert len(artifacts.scalars) == 51


def test_process_with_additional_data():
    artifacts = preprocessing.get_process("simple", "modex_tech_wind_turbine_onshore")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 12
    assert len(artifacts.scalars) == 51
    assert len(artifacts.timeseries.columns) == 4
    assert len(artifacts.timeseries) == 8760
    assert set(artifacts.timeseries.columns.get_level_values("name")) == {"wind_speed"}
    assert {item[0] for item in artifacts.timeseries.columns.get_level_values("region")} == {"HH", "HE", "NI", "MV"}


def test_process_with_additional_data_with_annotations():
    with utils.turn_on_annotations():
        artifacts = preprocessing.get_process("simple", "onshore wind farm")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 12
    assert len(artifacts.scalars) == 51
    assert len(artifacts.timeseries.columns) == 4
    assert len(artifacts.timeseries) == 8760
    assert set(artifacts.timeseries.columns.get_level_values("name")) == {"wind_speed"}
    assert {item[0] for item in artifacts.timeseries.columns.get_level_values("region")} == {"HH", "HE", "NI", "MV"}


def test_process_with_multiple_artifacts_for_process():
    artifacts = preprocessing.get_process("multiple_processes", "modex_tech_wind_turbine_onshore")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 13
    assert len(artifacts.scalars) == 51


def test_process_with_multiple_artifacts_for_process_with_annotations():
    with utils.turn_on_annotations():
        artifacts = preprocessing.get_process("multiple_processes", "onshore wind farm")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 13
    assert len(artifacts.scalars) == 51


def test_filter_df():
    data = {c: [c] for c in core.SCALAR_COLUMNS}
    data["a"] = [3]
    data["b"] = [5]
    df = pandas.DataFrame(data)
    adapter = preprocessing.Adapter(None)
    filtered_df = adapter._Adapter__filter_parameters(df, ("a",), collection.DataType.Scalar)
    del data["b"]
    expected_df = pandas.DataFrame(data)
    assert_frame_equal(filtered_df, expected_df)


def test_merge_regions():
    df = pandas.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "region": [["a", "b"], ["a"], ["b"], ["c"], ["d", "e"], ["a"]],
            "year": [1, 1, 1, 1, 1, 2],
            "value1": [10.0, None, 10.0, 3.0, 5.0, 4.0],
            "value2": [None, 2.0, 3.0, 5.0, 6.0, 4.0],
            "comment": [
                {"a": "a"},
                {"b": "a"},
                {"c": "a"},
                {"d": "a"},
                {"e": "a"},
                {"f": "a"},
            ],
            "method": [
                {"value1": "a"},
                {"value1": "c", "value2": "d"},
                {"value1": "b"},
                {},
                {"v1": "a"},
                {},
            ],
        },
    )
    adapter = preprocessing.Adapter(None)
    merged_regions = adapter._Adapter__merge_parameters(df.explode("region"), datatype=collection.DataType.Scalar)
    expected_df = pandas.DataFrame(
        {
            "region": ["a", "a", "b", "c", "d", "e"],
            "year": [1, 2, 1, 1, 1, 1],
            "value1": [10.0, 4.0, 10.0, 3.0, 5.0, 5.0],
            "value2": [2.0, 4.0, 3.0, 5.0, 6.0, 6.0],
            "comment": [
                {"a": "a", "b": "a"},
                {"f": "a"},
                {"a": "a", "c": "a"},
                {"d": "a"},
                {"e": "a"},
                {"e": "a"},
            ],
            "method": [
                {"value1": "a", "value2": "d"},
                {},
                {"value1": "a"},
                {},
                {"v1": "a"},
                {"v1": "a"},
            ],
        },
    )
    assert_frame_equal(merged_regions, expected_df)


def test_duplicate_values_in_merge_regions():
    df = pandas.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "region": [["a", "b"], ["a"], ["b"], ["c"], ["d", "e"]],
            "year": [1, 1, 1, 1, 1],
            "value1": [10.0, None, 2.0, 3.0, 5.0],
            "value2": [None, 2.0, 3.0, 5.0, 6.0],
            "comment": ["a", "b", "c", "d", "e"],
            "method": [
                {"value1": "a"},
                {"value1": "c", "value2": "d"},
                {"value1": "b"},
                {},
                {"v1": "a"},
            ],
        },
    )
    adapter = preprocessing.Adapter(None)
    with pytest.raises(preprocessing.PreprocessingError):
        adapter._Adapter__merge_parameters(df.explode("region"), datatype=collection.DataType.Scalar)


def test_refactor_timeseries():
    adapter = preprocessing.Adapter("refactor_timeseries")
    artifact = adapter.get_process("modex_capacity_factor")
    assert len(artifact.timeseries) == 8760 * 2
    assert len(artifact.timeseries.columns) == 16


def test_unit_conversion_in_scalar_data():
    adapter = preprocessing.Adapter("simple", units=["GW"])
    artifact = adapter.get_process("modex_tech_wind_turbine_onshore")
    assert artifact.scalars[artifact.scalars["region"] == "BE"].iloc[0]["installed_capacity"] == pytest.approx(
        11 / 1000
    )


def test_unit_conversion_in_timeseries_data():
    adapter = preprocessing.Adapter("simple", units=["GW"])
    artifact = adapter.get_process("modex_capacity_factor")
    assert artifact.timeseries[("onshore", ("HE",))].iloc[0] == pytest.approx(0.032336 / 1000, rel=1e-3)


def test_fks_with_multiple_versions():
    adapter = preprocessing.Adapter("fk_multiple_versions")
    artifact = adapter.get_process("ind_steel_casting_0")
    assert artifact.scalars["emissions_factor_sec_methane_ch4"][0] == 1
    assert artifact.scalars["emissions_factor_sec_methane_co2"][0] == 28


def test_fks_with_none_type():
    adapter = preprocessing.Adapter("process_type_none")
    artifact = adapter.get_process("ind_steel_casting_0")
    assert artifact.scalars["emissions_factor_sec_methane_co2"][0] == 28
    assert artifact.scalars["emissions_factor_sec_methane_ch4"][0] == 3
    assert artifact.scalars["emissions_factor_sec_methane_ch4"][1] == 2


def test_bandwidth_unpacking():
    adapter = preprocessing.Adapter("test_bandwidth")
    assert_series_equal(
        adapter.get_process("x2x_delivery_hydrogen_pipeline_new_1").scalars["conversion_factor_sec_hydrogen_orig"],
        pandas.Series([None, None, None, None, None, 1.0, 1.0, 1.0, 1.0, 1.0]),
        check_names=False,
    )
    assert_series_equal(
        adapter.get_process("x2x_delivery_hydrogen_pipeline_retrofit_1").scalars["conversion_factor_sec_hydrogen_orig"],
        pandas.Series([None, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
        check_names=False,
    )
