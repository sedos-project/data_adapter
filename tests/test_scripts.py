from data_adapter.scripts.sedos_structure_parser import parse_es_structure


def test_parse_es_structure():

    parse_es_structure(file_path="data_adapter/tests/test_data/test_structures/processes.csv")
    pass
