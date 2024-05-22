import json
import pathlib

from data_adapter import structure


def test_parameters():
    with open(
        pathlib.Path(__file__).parent / "test_data" / "test_structures" / "modex_example.json",
        encoding="utf-8",
    ) as hardcoded_json:
        dict_expected = json.load(hardcoded_json)

    st = structure.Structure("modex_example")
    assert st.parameters == dict_expected


def test_processes():
    st = structure.Structure("modex_example")
    assert len(st.processes) == 4
    assert st.processes["energy transformation unit"]["outputs"] == [["electricity", "heat"], "co2"]
