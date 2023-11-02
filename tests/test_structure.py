import json
import pathlib

from data_adapter import structure


def test_get_energy_structure():
    with open(
        pathlib.Path(__file__).parent / "test_data" / "test_structures" / "modex_example.json",
        encoding="utf-8",
    ) as hardcoded_json:
        dict_expected = json.load(hardcoded_json)

    assert structure.get_energy_structure(structure="modex_example") == dict_expected
