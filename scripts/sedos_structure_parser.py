import pandas as pd


def parse_es_structure(file_path: str, output_path: str) -> None:
    """
    Parses the es_structure in SEDOS project from two different B&W share tables.

    Parameters
    ----------
    file_path: str
        Path to B&W raw xlsx
    output_path: str
        Path to output file

    Returns
    -------
    None
    """

    # structure_file = settings.STRUCTURES_DIR / f"{default_structure}.csv"
    processes = pd.read_excel(
        io=file_path, engine="openpyxl", sheet_name="Processes", usecols=["Input", "Process", "Output"]
    )

    input_output = pd.read_excel(
        io=file_path, engine="openpyxl", sheet_name="input_output", usecols=["parameter", "process", "input", "output"]
    )

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

    # save to excel
    es_structure.to_excel(rf"{output_path}", index=False)

    return None


if __name__ == "__main__":
    parse_es_structure(
        file_path="SEDOS_Prozesse&Parameter.xlsx",
        output_path="SEDOS_es_structure.xlsx",
    )
