import os
import pathlib
os.environ["STRUCTURES_DIR"] = str(pathlib.Path(pathlib.Path.cwd() / "test_data/test_structures"))

from data_adapter.preprocessing import Structure

def test_get_commodity_diff():


    structure = Structure(
        "SEDOS_Modellstruktur",
        process_sheet="Processes_O1",
        parameter_sheet="Parameter_O1",
        helper_sheet="Helper_O1",
    )


    x = structure.get_commodity_diff()

    commodity_diff = {
        "sink_is_necessary": [
            "emi_CH4_f_ind",
            "emi_CO2_f_ind",
            "emi_N2O_f_ind",
            "emi_ch4_f_ind",
            "emi_ch4_p_x2x",
            "emi_co2_f_ind",
            "emi_co2_neg_imp",
            "emi_co2_p_x2x",
            "emi_co2_stored",
            "emi_n2o_f_ind",
            "emi_n2o_p_x2x",
            "iip_steel_blafu_slag",
            "pri_crude_oil",
            "pri_natural_gas",
            "sec_heat_district_high_cts",
            "sec_heat_district_high_hh",
            "sec_natural_gas_syn",
        ],
        "needed_from_external_source": ["emi_co2_neg_fuel_cc", "sec_heavy_fuel_oil"],
    }

    assert x == commodity_diff
