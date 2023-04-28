import pandas as pd


def read_sedos_bwshare_excel(file_path: str) -> dict:
    """
    Read SEDOS B&W-share excel file.

    Parameters
    ----------
    file_path
        Path to downloaded B&W share file.
    Returns
    -------
    dict of dataframes
    """
    processes = pd.read_excel(
        io=file_path, engine="openpyxl", sheet_name="Processes", usecols=["Input", "Process", "Output"]
    )

    input_output = pd.read_excel(
        io=file_path, engine="openpyxl", sheet_name="input_output", usecols=["parameter", "process", "input", "output"]
    )

    return {"processes": processes, "input_output": input_output}


def parse_es_structure(sedos_es_dict: dict) -> pd.DataFrame:
    """
    Parse the es_structure in SEDOS project from two different B&W share tables.

    Parameters
    ----------
    sedos_es_dict: dict
        Dict with dataframe of "processes" and "input_output" sheet

    Returns
    -------
    es_structure: pd.Dataframe
        Structure of energy system with default and parameter-specific inputs & outputs per process
    """

    processes = sedos_es_dict["processes"]
    input_output = sedos_es_dict["input_output"]

    inputs_outputs_default = pd.DataFrame(
        data={
            "parameter": "default",
            "process": processes.Process,
            "input": processes.Input,
            "output": processes.Output,
        }
    )

    es_structure = pd.concat([inputs_outputs_default, input_output], axis=0)

    # clean sheet and replace unwanted characters
    char_replace_dict = {"[": "", "]": "", "+": ",", " ": "", ".": "_"}
    for col in es_structure.columns:
        for key, value in char_replace_dict.items():
            es_structure[f"{col}"] = es_structure[f"{col}"].str.replace(key, value, regex=True)

    # sort values
    es_structure.sort_values(by=["process", "parameter"], inplace=True)
    es_structure.reset_index(inplace=True, drop=True)

    return es_structure


def write_es_structure_file(es_structure: pd.DataFrame, output_path: str) -> None:

    # save to excel
    es_structure.to_excel(rf"{output_path}", index=False)
