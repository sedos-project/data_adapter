import json
import pathlib

from data_adapter import structure


def test_get_energy_structure():
    with open(
        pathlib.Path(__file__).parent / "test_data" / "test_structures" / "modex_example.json",
        "r",
        encoding="utf-8",
    ) as hardcoded_json:
        dict_expected = json.load(hardcoded_json)

    assert structure.get_energy_structure(structure="modex_example") == dict_expected


def test_get_links():
    links = structure.get_links("hack-a-thon_links")
    assert len(links) == 3
    assert "modex_tech_generator_gas" in links
    assert len(links["modex_tech_generator_gas"]) == 2
    assert isinstance(links["modex_tech_generator_gas"][0], structure.Link)
    assert links["modex_tech_generator_gas"][0].linked_process == "modex_constraint"
    assert links["modex_tech_generator_gas"][0].parameter == "emission_costs"


def test_get_links_for_process():
    links = structure.get_links_for_process("modex_tech_wind_turbine_onshore", "hack-a-thon_links")
    assert len(links) == 2
    assert links["modex_capacity_factor"] == ["onshore"]
    assert links["modex_constraint"] == ["wacc"]
