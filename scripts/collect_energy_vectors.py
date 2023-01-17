"""
This script collects the energy vectors for multiple input and output technologies from a csv in a pandas dataframe.

It outputs 5 csv tables for the database.

From here
https://bwsyncandshare.kit.edu/apps/onlyoffice/2458081675?filePath=%2FSEDOS%2FProjektinhalte%2FAP3_Modellstruktur%2FSEDOS_Prozesse%26Parameter.xlsx
"""

import re

import pandas as pd

MAX_IDENTIFIER_LENGTH = 50
# pylint:disable=C0209
IDENTIFIER_PATTERN = re.compile(
    "^[a-z][a-z0-9_, ]{0,%s}$" % (MAX_IDENTIFIER_LENGTH - 1)
)

# list for collection of missing energy vectors
MISSING_IO = []


def check_colum_character_convention(dataframe=None):
    for col in dataframe.columns[1:]:
        for element in dataframe[col]:
            if not IDENTIFIER_PATTERN.match(element):
                raise ValueError(
                    f"Wrong syntax: {element}\nAllowed are characters: a-z and 0-9 and , and _"
                )


def check_energy_vector_exists(set_io=None, subset_io=None):
    for vec in subset_io:
        if vec not in set_io:
            MISSING_IO.append(vec)


def parse_mimo_process_parameters_to_db(
    in_out_path: str = None, parameter_process_path: str = None, engine=None
) -> None:
    """
    Parse process and its parameters with corresponding inputs and outputs to database.

    Parameters
    ----------
    in_out_path: str
        Path to input and output sheet.
    parameter_process_path: str
        Path to process and parameter sheet.
    engine
        Define engine.
    Returns
    -------
    ValueError
        if processes of parameters do not match character convention
        if inputs or outputs are unknown
    """

    # read multiple input and output csv & input/output table
    mimo = pd.read_csv(parameter_process_path, delimiter=";", encoding="utf-8")
    check_colum_character_convention(mimo)

    input_output = pd.read_csv(in_out_path, delimiter=";", encoding="utf-8")
    INPUT_OUTPUT = set(input_output["name"])

    # create process table
    process = mimo[["process"]].copy()
    process.drop_duplicates(subset=["process"], inplace=True)
    process.reset_index(inplace=True, drop=True)
    process.reset_index(inplace=True, names="id")

    # create parameters table
    parameters = mimo[["parameter", "process"]].copy()
    parameters["process_id"] = parameters["process"].map(
        process.set_index("process")["id"]
    )
    parameters.rename(columns={"parameter": "name"}, inplace=True)
    parameters.reset_index(level=0, names="id", inplace=True)
    parameters = parameters[["id", "process_id", "name"]]

    # create input table
    df_input_raw = mimo[["parameter", "input"]].copy()
    df_input_raw["input"] = df_input_raw["input"].str.split(",")
    df_input_raw = df_input_raw.explode("input")
    df_input_raw["input"] = df_input_raw["input"].apply(lambda x: x.strip())
    df_input_raw.reset_index(level=0, inplace=True, drop=True)
    check_energy_vector_exists(
        set_io=INPUT_OUTPUT, subset_io=set(df_input_raw["input"])
    )

    df_input_parameters = (
        df_input_raw.merge(parameters, left_on="parameter", right_on="name")
        .reindex(columns=["id", "input"])
        .rename(columns={"id": "parameter_id"})
    )
    df_input_final = (
        df_input_parameters.merge(input_output, left_on="input", right_on="name")
        .rename(columns={"id": "commodity_id"})
        .reindex(columns=["parameter_id", "commodity_id"])
    )

    # create output table
    df_output_raw = mimo[["parameter", "output"]].copy()
    df_output_raw["output"] = df_output_raw["output"].str.split(",")
    df_output_raw = df_output_raw.explode("output")
    df_output_raw["output"] = df_output_raw["output"].apply(lambda x: x.strip())
    df_output_raw.reset_index(level=0, inplace=True, drop=True)
    check_energy_vector_exists(
        set_io=INPUT_OUTPUT, subset_io=set(df_output_raw["output"])
    )

    df_output_parameters = (
        df_output_raw.merge(parameters, left_on="parameter", right_on="name")
        .reindex(columns=["id", "output"])
        .rename(columns={"id": "parameter_id"})
    )
    df_output_final = (
        df_output_parameters.merge(input_output, left_on="output", right_on="name")
        .rename(columns={"id": "commodity_id"})
        .reindex(columns=["parameter_id", "commodity_id"])
    )

    # check missing energy vectors exist before import to db
    if MISSING_IO:
        raise ValueError(f"Not in INPUT_OUTPUT: {MISSING_IO}")

    # tables to database
    process.to_sql("process", con=engine, index=False, if_exists="replace")
    parameters.to_sql("parameter", con=engine, index=False, if_exists="replace")
    df_input_final.to_sql(
        "parameter_inputs", con=engine, index=False, if_exists="replace"
    )
    df_output_final.to_sql(
        "parameter_outputs", con=engine, index=False, if_exists="replace"
    )
    input_output.to_sql("input_output", con=engine, index=False, if_exists="replace")
