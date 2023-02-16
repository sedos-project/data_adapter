import os

import pytest
from sqlalchemy.orm import Session

from data_adapter import settings, structure
from data_adapter.structure import get_energy_structure


@pytest.fixture()
def _setup_db():
    structure.init_database()
    yield
    # Remove test.db after tests
    if settings.DATABASE_URL.startswith("sqlite"):
        test_db = settings.DATABASE_URL.split("///")[1]
        os.remove(test_db)  # Set breakpoint here to check sqlite DB before removal


@pytest.mark.usefixtures("_setup_db")
def test_es_example():
    with Session(settings.engine) as session:
        gas_turbine = structure.Process(name="gas turbine")
        gas_bus = structure.InputOutput(name="gas")
        electricity_bus = structure.InputOutput(name="electricity")
        session.add_all((gas_bus, electricity_bus, gas_turbine))
        session.flush()
        input_ratio = structure.Parameter(name="input_ratio", process_id=gas_turbine.id)
        input_ratio.inputs.append(gas_bus)
        input_ratio.outputs.append(electricity_bus)
        session.add(input_ratio)
        session.commit()


def test_get_energy_structure():

    dict_expected = {
        "chp": {
            "eff_heat": {"inputs": ["gas", "coal"], "outputs": ["heat", "co2"]},
            "eff_elec": {"inputs": ["biomass", "gas"], "outputs": ["elec", "co2"]},
        },
        "empty_out": {"para": {"inputs": ["in1", "in2"], "outputs": []}},
        "empty_in": {"para": {"inputs": [], "outputs": ["out"]}},
    }

    assert (
        get_energy_structure(
            process_parameter_path="test_data/test_mimo/user_mimos.csv"
        )
        == dict_expected
    )
