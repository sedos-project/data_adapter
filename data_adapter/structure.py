from __future__ import annotations

import re
from collections import defaultdict, namedtuple

import pandas as pd

from data_adapter import settings

MAX_IDENTIFIER_LENGTH = 50

# pylint:disable=C0209
IDENTIFIER_PATTERN = re.compile("^[a-z][a-z0-9_, ]{0,%s}$" % (MAX_IDENTIFIER_LENGTH - 1))


class StructureError(Exception):
    """Raised if structure is corrupted"""


AdditionalParameter = namedtuple("AdditionalParameter", ("subject", "isAbout"))

ADDITONAL_PARAMETERS = {
    "onshore wind farm": [
        AdditionalParameter("net capacity factor", "onshore"),
    ]
}


def get_additional_parameters(process: str):
    if process not in ADDITONAL_PARAMETERS:
        return {}
    parameters = defaultdict(list)
    for parameter in ADDITONAL_PARAMETERS[process]:
        parameters[parameter.subject].append(parameter.isAbout)
    return parameters


def check_character_convention(dataframe: pd.DataFrame):
    """
    Check in parameter-, process-, input-and output-column for character convention.

    Parameters
    ----------
    dataframe: pandas.DataFrame
        Parameters in dataframe are checked for convention

    Raises
    ------
    ValueError
        if element in dataframe does not fit character convention

    """
    for col in dataframe.columns[1:]:
        for element in dataframe[col]:
            if not isinstance(element, str):
                continue
            if not IDENTIFIER_PATTERN.match(element):
                raise ValueError(f"Wrong syntax: {element}\nAllowed are characters: a-z and 0-9 and , and _")


def get_energy_structure(structure: str) -> dict:
    """
    Parse processes and its parameters with corresponding inputs and outputs to dict.

    Parameters
    ----------
    structure: str
        Name of structure to look up in structure folder

    Returns
    -------
    dict
        Energy modelling processes, its parameters and inputs and output
    """
    structure_file = settings.STRUCTURES_DIR / f"{structure}.csv"
    process_parameter_in_out = pd.read_csv(
        filepath_or_buffer=structure_file,
        delimiter=";",
        encoding="utf-8",
        usecols=["parameter", "process", "inputs", "outputs"],
    )
    check_character_convention(process_parameter_in_out)

    # create ES_STRUCTURE dict from process_parameter_in_out
    list_dic = process_parameter_in_out.to_dict(orient="records")

    es_structure = {}

    for dic in list_dic:
        dic_para = {}

        if isinstance(dic.get("inputs"), str):
            inputs = {"inputs": dic.get("inputs").replace(" ", "").split(",")}
        else:
            inputs = {"inputs": []}
        if isinstance(dic.get("outputs"), str):
            outputs = {"outputs": dic.get("outputs").replace(" ", "").split(",")}
        else:
            outputs = {"outputs": []}

        dic_para[dic.get("parameter")] = inputs | outputs

        if dic.get("process") not in es_structure:
            es_structure[dic.get("process")] = dic_para
        else:
            es_structure[dic.get("process")] = es_structure[dic.get("process")] | dic_para

    return es_structure


def get_processes(structure: str):
    return list(get_energy_structure(structure))
