import pandas as pd
from pandas.testing import assert_frame_equal

from scripts.sedos_structure_parser import parse_es_structure, read_sedos_bwshare_excel


def test_parse_es_structure():
    data = {
        "parameter": ["ACT_BND", "ACT_COST", "FLO_EFF", "default", "default", "default", "default"],
        "process": [
            "ind_cement_rk_ccs_1",
            "ind_cement_rk_ccs_1",
            "ind_cement_rk_ccs_1",
            "pow_combustion_gt",
            "pow_combustion_gt_SNG",
            "pow_combustion_gt_biogas",
            "pow_combustion_gt_natgas",
        ],
        "input": [
            "coal,coke,coke_oven_gas,heavy_fuel_oil,natgas,hydrogen,SNG,,biomass,waste,sludge,elec,"
            "cement_rawmeal_mats",
            "coal,coke,coke_oven_gas,heavy_fuel_oil,natgas,hydrogen,SNG,,biomass,"
            "waste,sludge,elec,cement_rawmeal_mats",
            "coal,coke,coke_oven_gas,heavy_fuel_oil,natgas,hydrogen,SNG,,biomass,waste,sludge,elec,cement_rawmeal_mats",
            "biogas,natgas,SNG_ren,SNG_conv,hydrogen_ren,hydrogen_conv,heating_oil",
            "SNG_ren,SNG_conv",
            "biogas",
            "natgas",
        ],
        "output": [
            "cement_clinker_mats,CO2p,CO2f,CH4f,N2Of",
            "cement_clinker_mats,CO2p,CO2f,CH4f,N2Of",
            "cement_clinker_mats,CO2p,CO2f,CH4f,N2Of",
            "elec_ren,elec_conv,CO2",
            "elec_ren,elec_conv,CO2",
            "elec_ren",
            "elec_conv,CO2",
        ],
    }
    expected_output = pd.DataFrame(data)

    function_df = parse_es_structure(
        sedos_es_dict=read_sedos_bwshare_excel("test_data/test_structures/SEDOS_Prozesse&Parameter.xlsx")
    )

    assert_frame_equal(expected_output, function_df)
