import pandas as pd

from scripts.sedos_structure_parser import parse_es_structure


def test_parse_es_structure():
    expected_output = pd.read_excel(r"test_data\test_structures\SEDOS_es_structure.xlsx")

    print(expected_output.parameter)
    parse_es_structure(
        file_path=r"test_data\test_structures\SEDOS_Prozesse&Parameter.xlsx",
        output_path=r"test_data\test_structures\SEDOS_es_structure_test_output.xlsx",
    )

    func_output = pd.read_excel(r"test_data\test_structures\SEDOS_es_structure_test_output.xlsx")

    assert expected_output == func_output
