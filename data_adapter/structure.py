from __future__ import annotations

import re
from typing import List, Optional

import pandas as pd

from data_adapter import settings

MAX_IDENTIFIER_LENGTH = 50

# pylint:disable=C0209
IDENTIFIER_PATTERN = re.compile("^[a-z][a-z0-9_, ]{0,%s}$" % (MAX_IDENTIFIER_LENGTH - 1))


class StructureError(Exception):
    """Raised if structure is corrupted."""


def check_character_convention(dataframe: pd.DataFrame, cols: Optional[List[str]] = None) -> pd.DataFrame:
    """Check in parameter-, process-, input-and output-column for character convention.

    Parameters
    ----------
    dataframe: pandas.DataFrame
        Parameters in dataframe are checked for convention
    cols: Optional[List[str]]
        Columns to check for

    Raises
    ------
    ValueError
        if element in dataframe does not fit character convention

    """
    cols = dataframe.columns if cols is None else cols
    for col in cols:
        for element in dataframe[col]:
            if not isinstance(element, str):
                continue
            if not IDENTIFIER_PATTERN.match(element):
                raise ValueError(f"Wrong syntax: {element}\nAllowed are characters: a-z and 0-9 and , and _")


class Structure:
    def __init__(self, structure_name: str):
        self.structure_file = settings.STRUCTURES_DIR / f"{structure_name}.xlsx"
        self.processes = self._init_processes()
        self.parameters = self._init_parameters()

    def _init_processes(self):
        def get_nodes(nodes_raw):
            nodes_raw_stripped = nodes_raw.replace(" ", "")
            grouped_nodes_raw = re.findall(r"\[[\w*,\,]*]", nodes_raw_stripped)

            nodes = []
            for group in grouped_nodes_raw:
                nodes.append(get_nodes(group[1:-1]))  # without brackets
                # Remove groups
                nodes_raw_stripped = nodes_raw_stripped.replace(group, "")
            nodes += [node for node in nodes_raw_stripped.split(",") if node != ""]
            return nodes

        process_parameter_in_out = pd.read_excel(
            io=self.structure_file,
            sheet_name="Process_Set",
            usecols=("process", "input", "output"),
        )
        check_character_convention(process_parameter_in_out, ["process"])
        processes = process_parameter_in_out.to_dict(orient="records")
        return {
            process["process"]: {"inputs": get_nodes(process["input"]), "outputs": get_nodes(process["output"])}
            for process in processes
        }

    def _init_parameters(self):
        """Parse processes and its parameters with corresponding inputs and outputs to dict.

        Returns
        -------
        dict
            Energy modelling processes, its parameters and inputs and output
        """
        process_parameter_in_out = pd.read_excel(
            io=self.structure_file,
            sheet_name="Parameter_Input-Output",
            usecols=("parameter", "process", "inputs", "outputs"),
        )
        check_character_convention(process_parameter_in_out, ["process", "inputs", "outputs"])

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
