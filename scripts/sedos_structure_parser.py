import pandas as pd
import re

total_list = []

df_com = pd.read_excel(
    io=r"C:\Users\christoph.muschner\CWM\Python\SEDOS\SEDOS_Modellstruktur.xlsx",
    engine="openpyxl",
    sheet_name="Nomenclature_Commodities",
    usecols=["old name", "new name suggestion"],
)

process_set = pd.read_excel(
    io=r"C:\Users\christoph.muschner\CWM\Python\SEDOS\SEDOS_Modellstruktur.xlsx", engine="openpyxl",
    sheet_name="Process_Set", usecols=["input", "process", "output"]
)


def replace_string(row):

    if not isinstance(row, str):
        print("Row is type:", type(row), row)
        row = ""
        return row

    commodity_mapping = dict(zip(df_com["old name"], df_com["new name suggestion"]))

    row_list = re.split(",|\+", row)

    new_list = [commodity_mapping.get(value, value) for value in row_list]

    common_list = list(set(row_list).intersection(new_list))

    if common_list:
        total_list.extend(common_list)

    replaced_row = ", ".join([str(elem) for elem in new_list])

    return replaced_row

def map_old_to_new_commodity_names():

    char_replace_dict = {"[": "", "]": "", "+": ",", " ": "", ".": "_", "  ": ""}
    for col in process_set.columns:
        for key, value in char_replace_dict.items():
            process_set[f"{col}"] = process_set[f"{col}"].str.replace(key, value, regex=True)

    cols = ["input", "output"]

    for col in cols:
        process_set[f"{col}"] = process_set[f"{col}"].apply(replace_string)

    process_set.to_csv(r"C:\Users\christoph.muschner\CWM\Python\SEDOS_DB\process_set_new_com.csv", sep=";")

    return process_set


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
