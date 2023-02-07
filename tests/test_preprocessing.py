from data_adapter import preprocessing


def test_process():
    artifacts = preprocessing.get_process_df("test_collection", "battery storage")
    assert len(artifacts) == 1
    assert "modex_tech_storage_battery" in artifacts
    data = artifacts["modex_tech_storage_battery"]
    assert len(data.columns) == 16
    assert len(data) == 30


def test_process_with_additional_data():
    artifacts = preprocessing.get_process_df("test_collection", "onshore wind farm")
    assert len(artifacts) == 2
    assert "modex_tech_wind_turbine_onshore" in artifacts
    assert "modex_capacity_factor" in artifacts
    assert len(artifacts["modex_tech_wind_turbine_onshore"].columns) == 12
    assert len(artifacts["modex_tech_wind_turbine_onshore"]) == 51
    assert len(artifacts["modex_capacity_factor"].columns) == 9
    assert len(artifacts["modex_capacity_factor"]) == 4
    assert len(artifacts["modex_capacity_factor"]["onshore"].dropna().iloc[0]) == 8760
