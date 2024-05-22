from __future__ import annotations

import re
from typing import List, Optional

import pandas as pd
from openpyxl import load_workbook
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from data_adapter import settings

MAX_IDENTIFIER_LENGTH = 50

# pylint:disable=C0209
IDENTIFIER_PATTERN = re.compile("^[a-z][a-z0-9_, ]{0,%s}$" % (MAX_IDENTIFIER_LENGTH - 1))


class StructureError(Exception):
    """Raised if structure is corrupted."""


def check_character_convention(dataframe: pd.DataFrame, cols: Optional[List[str]] = None):
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
    def __init__(
        self,
        structure_name: str,
        process_sheet: str = "Process_Set",
        parameter_sheet: str = "Parameter_Input-Output",
        helper_sheet: str = "Helper_Set",
    ):
        self.structure_file = settings.STRUCTURES_DIR / f"{structure_name}.xlsx"
        self.processes = self._init_processes(process_sheet, helper_sheet)
        self.parameters = self._init_parameters(parameter_sheet)

    def _init_processes(self, process_sheet: str, helper_sheet: str) -> dict:
        """Parse (helper) processes with corresponding inputs and outputs to dict.

        Parameters
        ----------
        process_sheet: str
            Sheet to read processes from
        helper_sheet: str
            Sheet to read additional helper processes from

        Returns
        -------
        dict
            Energy modelling processes and related inputs and outputs
        """

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

        processes_raw = pd.read_excel(
            io=self.structure_file,
            sheet_name=process_sheet,
            usecols=("process", "input", "output"),
        )
        wb = load_workbook(self.structure_file, read_only=True)
        if helper_sheet in wb.sheetnames:
            helpers_raw = pd.read_excel(
                io=self.structure_file,
                sheet_name=helper_sheet,
                usecols=("process", "input", "output"),
            )
            processes_raw = pd.concat([processes_raw, helpers_raw])
        processes_raw = processes_raw.fillna("")
        check_character_convention(processes_raw, ["process"])
        processes = processes_raw.to_dict(orient="records")
        return {
            process["process"]: {"inputs": get_nodes(process["input"]), "outputs": get_nodes(process["output"])}
            for process in processes
        }

    def _init_parameters(self, parameter_sheet: str) -> dict:
        """Parse processes and its parameters with corresponding inputs and outputs to dict.

        Parameters
        ----------
        parameter_sheet: str
            Sheet to read parameters from

        Returns
        -------
        dict
            Energy modelling processes, its parameters and inputs and output
        """
        process_parameter_in_out = pd.read_excel(
            io=self.structure_file,
            sheet_name=parameter_sheet,
            usecols=("parameter", "process", "inputs", "outputs"),
        )
        process_parameter_in_out = process_parameter_in_out.fillna("")
        check_character_convention(process_parameter_in_out, ["process", "parameter"])

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

    def plot_commodity_interfaces(self, categories: list = ['pri', 'sec', 'iip', 'exo', 'emi'], sectors: list = ['pow', 'x2x', 'ind', 'mob', 'hea', "helper"]):

        cols = len(categories)

        # Create plotting object
        fig, axes = plt.subplots(nrows=1, ncols=cols, figsize=(cols * 10, 16), sharey=False)
        if len(categories) == 1:
            axes = [axes]  # Wrap the single AxesSubplot object in a list for indexing

        # Initialize dictionaries to store the commodities for each sector
        for i, category in enumerate(categories):
            input_commodities = {sector: set() for sector in sectors}
            output_commodities = {sector: set() for sector in sectors}

            # Iterate over the rows and populate the dictionaries
            for process_name, io_dict in self.processes.items():
                row_sectors = [process_name.split("_")[0]]
                inputs = [num for item in io_dict["inputs"] for num in (item if isinstance(item, list) else (item,))]
                outputs = [num for item in io_dict["outputs"] for num in (item if isinstance(item, list) else (item,))]
                categories_set = set([category.split("_")[0] for category in inputs + outputs])
                # level io dict values
                for sector in row_sectors:
                    if category in categories_set:
                        input_commodities[sector] |= set(
                            [commodity for commodity in inputs if commodity.startswith(category)])
                        output_commodities[sector] |= set(
                            [commodity for commodity in outputs if commodity.startswith(category)])

            # Create the matrix visualization for the current category
            combined = {sector: list(input_commodities[sector] | output_commodities[sector]) for sector in sectors}
            unique_commodity_list = sorted(list(set(commodity for sector in combined.values() for commodity in sector)))

            # Create a DataFrame with initial values of 0
            matrix_data = pd.DataFrame(np.NaN, index=unique_commodity_list, columns=sectors)

            # Update the DataFrame with -1 for input, 1 for output, and 0 for both
            for sector in sectors:
                for commodity in combined[sector]:
                    if commodity in input_commodities[sector] and commodity in output_commodities[sector]:
                        matrix_data.at[commodity, sector] = 0
                    elif commodity in input_commodities[sector]:
                        matrix_data.at[commodity, sector] = -1
                    elif commodity in output_commodities[sector]:
                        matrix_data.at[commodity, sector] = 1

            # Plot the matric information
            ax = axes[i]
            im = ax.imshow(matrix_data.values, cmap='RdYlGn', vmin=-1, vmax=1)

            # Create a frame around each cell in the matrix for better readability
            for j in range(len(matrix_data.index)):
                for k in range(len(matrix_data.columns)):
                    value = matrix_data.values[j, k]
                    color = 'white' if np.isnan(
                        value) else 'red' if value == -1 else 'green' if value == 1 else 'yellow'
                    rect = plt.Rectangle((k - 0.5, j - 0.5), 1, 1, fill=True, facecolor=color, edgecolor='black',
                                         linewidth=1)
                    ax.add_patch(rect)

            # Labeling
            plt.sca(axes[i])
            ax.set_xticks(range(len(matrix_data.columns)), matrix_data.columns)
            ax.set_yticks(range(len(matrix_data.index)), matrix_data.index)
            ax.set_xlabel('Sectors', fontsize=12)
            ax.set_title(category.upper(), fontsize=16)

        # Create a legend for the colors
        legend_elements = [
            Patch(facecolor='white', edgecolor='black', label='No Relation'),
            Patch(facecolor='red', edgecolor='black', label='Input'),
            Patch(facecolor='green', edgecolor='black', label='Output'),
            Patch(facecolor='yellow', edgecolor='black', label='Input & Output')]
        fig.legend(handles=legend_elements, loc='upper left', fontsize=12)
        plt.tight_layout()

        # Save the plot as svg
        plt.show()

    def get_commodity_diff(self, input_processes:list = ["source", "import"], output_processes:list= ["sink"]):
        d = {"inputs": [], "outputs": []}
        for x in self.processes.values():
            inputs = x["inputs"]
            outputs = x["outputs"]

            # If nested value level and add to io_dict
            for i in inputs:
                if isinstance(i, list):
                    for in_list in i:
                        d["inputs"].append(in_list)
                else:
                    d["inputs"].append(i)
            for o in outputs:
                if isinstance(o, list):
                    for out_list in o:
                        d["outputs"].append(out_list)
                else:
                    d["outputs"].append(o)

        # delete duplicates
        d["inputs"] = np.unique(np.array(d["inputs"]))
        d["outputs"] = np.unique(d["outputs"])

        needed_from_external_source = [x for x in d["inputs"] if x not in d["outputs"]]
        sink_is_necessary = [x for x in d["outputs"] if x not in d["inputs"]]

        for process, io in self.processes.items():
            for count, x in enumerate(needed_from_external_source):
                if x in io["inputs"] and any([ip in process for ip in input_processes]):
                    needed_from_external_source.pop(count)
            for x in sink_is_necessary:
                if x in io["outputs"] and any([op in process for op in output_processes]):
                    sink_is_necessary = sink_is_necessary - x

        return {"sink_is_necessary": sink_is_necessary, "needed_from_external_source": needed_from_external_source}
