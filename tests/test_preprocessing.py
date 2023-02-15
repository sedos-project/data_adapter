import pandas
import pytest
from pandas.testing import assert_frame_equal

from data_adapter import collection, core, preprocessing, structure


def test_process():
    artifacts = preprocessing.get_process("simple", "battery storage")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 16
    assert len(artifacts.scalars) == 48


def test_process_with_additional_data():
    artifacts = preprocessing.get_process("simple", "onshore wind farm")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 12
    assert len(artifacts.scalars) == 48
    assert len(artifacts.timeseries.columns) == 9
    assert len(artifacts.timeseries) == 4
    assert len(artifacts.timeseries["onshore"].dropna().iloc[0]) == 8760


def test_process_with_multiple_artifacts_for_process():
    structure.ADDITONAL_PARAMETERS = {}
    artifacts = preprocessing.get_process("multiple_processes", "onshore wind farm")
    assert hasattr(artifacts, "scalars")
    assert hasattr(artifacts, "timeseries")
    assert len(artifacts.scalars.columns) == 13
    assert len(artifacts.scalars) == 48
    assert len(artifacts.timeseries) == 0


def test_filter_df():
    data = {c: [c] for c in core.SCALAR_COLUMNS}
    data["a"] = [3]
    data["b"] = [5]
    df = pandas.DataFrame(data)
    filtered_df = preprocessing._filter_parameters(df, ("a",), collection.DataType.Scalar)
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
    merged_regions = preprocessing._merge_parameters(df.explode("region"), datatype=collection.DataType.Scalar)
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
        preprocessing._merge_parameters(df.explode("region"), datatype=collection.DataType.Scalar)
