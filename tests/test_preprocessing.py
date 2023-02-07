import pandas
import pytest
from pandas.testing import assert_frame_equal

from data_adapter import collection, core, preprocessing


def test_process():
    artifacts = preprocessing.get_process_df("test_collection", "battery storage")
    assert len(artifacts) == 1
    assert "modex_tech_storage_battery" in artifacts
    data = artifacts["modex_tech_storage_battery"]
    assert len(data.columns) == 16
    assert len(data) == 48


def test_process_with_additional_data():
    artifacts = preprocessing.get_process_df("test_collection", "onshore wind farm")
    assert len(artifacts) == 2
    assert "modex_tech_wind_turbine_onshore" in artifacts
    assert "modex_capacity_factor" in artifacts
    assert len(artifacts["modex_tech_wind_turbine_onshore"].columns) == 12
    assert len(artifacts["modex_tech_wind_turbine_onshore"]) == 48
    assert len(artifacts["modex_capacity_factor"].columns) == 9
    assert len(artifacts["modex_capacity_factor"]) == 4
    assert len(artifacts["modex_capacity_factor"]["onshore"].dropna().iloc[0]) == 8760


def test_filter_df():
    data = {c: [c] for c in core.SCALAR_COLUMNS}
    data["a"] = [3]
    data["b"] = [5]
    df = pandas.DataFrame(data)
    filtered_df = preprocessing._filter_parameters(
        df, ("a",), collection.DataType.Scalar
    )
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
        }
    )
    merged_regions = preprocessing._merge_regions(
        df, datatype=collection.DataType.Scalar
    )
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
        }
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
        }
    )
    with pytest.raises(preprocessing.PreprocessingError):
        preprocessing._merge_regions(df, datatype=collection.DataType.Scalar)
