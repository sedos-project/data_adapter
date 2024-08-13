from data_adapter import unit_conversion


def test_unit_conversion():
    assert unit_conversion.get_conversion_factor("vehicles", "kvehicles") == 1 / 1000
    assert unit_conversion.get_conversion_factor("GWh", "kWh") == 1e6
    assert unit_conversion.get_conversion_factor("Gp", "p") == 1e9
