from data_adapter.structure import get_energy_structure


def test_get_energy_structure():
    dict_expected = {
        "chp": {
            "eff_heat": {"inputs": ["gas", "coal"], "outputs": ["heat", "co2"]},
            "eff_elec": {"inputs": ["biomass", "gas"], "outputs": ["elec", "co2"]},
        },
        "empty_out": {"para": {"inputs": ["in1", "in2"], "outputs": []}},
        "empty_in": {"para": {"inputs": [], "outputs": ["out"]}},
    }

    assert get_energy_structure(structure="user_mimos") == dict_expected
