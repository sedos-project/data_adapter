import os
from collections import defaultdict, namedtuple

from dataclasses import dataclass, field
import graphviz
import json
import csv
import pandas as pd
from MultiChoice import MultiChoice

from databus import download_collection


# download_collection(collection_url = "https://energy.databus.dbpedia.org/felixmaur/collections/modex_test_renewable")

class StructureError(Exception):
    """Raised if structure is corrupted"""


def remove_duplicates_from_list(lst: list = ["None"]):
    f


@dataclass
class ES_STRUCT:
    collection_dict: dict
    collection_path: str = "../collections/modex_test_renewable"
    tech: list = field(init=False)
    tech_names: list = field(init=False)
    listdir: list = field(init=False)

    def __post_init__(self):
        self.tech = [element for i in self.collection_dict.values() for element in i if "tech" in element]
        self.tech_names = [element for i in self.collection_dict for element in i]


this_path = "../collections/hack-a-thon/"
HARDCODED_ES_STUCT = {}
with open(this_path + "collection.json") as f:
    for source, element_dict in json.load(f).items():
        for element, value in element_dict.items():
            if "tech" in element:
                lastest_version_csv_path = this_path + source + "/" + element + "/" + value[
                    "latest_version"] + "/" + element + ".csv"
                io_list = pd.read_csv(lastest_version_csv_path).drop(["id", "region", "method", "source", "comment",
                                                                      "year",
                                                                      "bandwidth_type", "lifetime", "version",
                                                                      "capital_costs", "fixed_costs", "marginal_costs",
                                                                      "variable_costs"],
                                                                     axis=1, errors="ignore").columns.values.tolist()

                io_dict = {}
                for io in io_list:
                    io_dict[io] = {}
                    # options = ("electricity", "ch4", "wind_onshore_capacity_factor",
                    #            "wind_offshore_capacity_factor", "solar_capacity_factor", "coal")
                    # inputs = input(f"Give inputs for {element}, {io} seperated by coma")
                    # if inputs.split(",") not in options:
                    #     Exception(KeyError, f"{inputs} not in options")
                    # outputs = input(f"Give outputs for {element}, {io} seperated by coma")
                    # if outputs.split(",") not in options:
                    #     Exception(KeyError, f"{outputs} not in options")
                    io_dict[io]["inputs"] = []
                    io_dict[io]["outputs"] = []
                    # for i in inputs.split(","):
                    #     io_dict[io]["inputs"].append(i)
                    #     for i in outputs.split(","):
                    #         io_dict[io]["outputs"].append(i)

                HARDCODED_ES_STUCT[element] = io_dict

print(HARDCODED_ES_STUCT)
with open(this_path + "HARDCODED_ES_STRUCT.json", "w") as f:
    json.dump(HARDCODED_ES_STUCT, f)
exit()

HARDCODED_ES_STRUCTURE = {
    # dispatchables:
    "ch4-gt": {
        "capacity": {"inputs": ["ch4"], "outputs": ["electricity"]},
        "efficiency": {"inputs": ["ch4"], "outputs": ["electricity"]},
    },
    "electricity-liion_battery": {
        "storage_capacity": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "capacity": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "storage_capacity_initial": {"inputs": ["electricity"], "outputs": ["electricity"]},
    },
    # timeseries dependend (with profiles):
    # version 1 for wind-onshore:
    "wind-onshore1": {
        "profile": {"inputs": ["wind-profile"], "outputs": ["electricity"]},
        "capacity": {"inputs": ["wind-profile"], "outputs": ["electricity"]},
    },
    # version 2 for wind-onshore:
    "wind-onshore2": {
        "capacity": {"inputs": ["wind-profile"], "outputs": ["electricity"]},
    },
    "electricity-demand": {
        "profile": {"inputs": ["electricity-load-profile"], "outputs": ["electricity"]},
    },

}

Parameter = namedtuple("Parameter", ("subject", "isAbout"))

ADDITONAL_PARAMETERS = {
    "onshore wind farm": [
        Parameter("net capacity factor", "onshore"),
    ]
}


def get_additional_parameters(process: str):
    if process not in ADDITONAL_PARAMETERS:
        return {}
    parameters = defaultdict(list)
    for parameter in ADDITONAL_PARAMETERS[process]:
        parameters[parameter.subject].append(parameter.isAbout)
    return parameters


def get_energy_structure():
    return HARDCODED_ES_STRUCTURE


def get_processes():
    return list(HARDCODED_ES_STRUCTURE)


def draw_struct_graphviz(HARDCODED_ES_STRUCTURE: dict, ADDITONAL_PARAMETERS: dict) -> graphviz.Digraph():
    """

    Parameters
    ----------
    HARDCODED_ES_STRUCTURE
    ADDITONAL_PARAMETERS

    Returns
    -------
    Graphviz object

    How To
    ------
    Graphviz graphs are created by a string. The String is build with trigger string characters representing line and
    column breaks.

        Linebreaks:

    TODO:
        - Layout verbessern
        - verschaltete Prozesse mit Unterprozessen verbinden (input/output zusammenhang: gas -> input -> output -> elec)

    """

    s = graphviz.Digraph('wide', filename='structs_revisited.gv',
                         node_attr={'shape': 'record'}, graph_attr={"nodesep": "1"}, engine='dot')

    def cluster():
        """
        Examining Clusters
            Pro:
                - Able to draw nice boxes around Process clusters
                - Easy understandable
            Cons:
                - Somehow boxes do not appear if subprocesses are not interconnected (
                    maybe add invisible edges between processes?)
                - Maybe use "cluster_edges"?
                - Duplicate processes seem not possible on first view -> ineligible solution!
        Returns
        -------
        graphviz.Digraph() object

        """
        for struct, process in HARDCODED_ES_STRUCTURE.items():
            with s.subgraph(name=struct) as c:
                edges = []
                for process_name, process_vars in process.items():
                    for inpts in process_vars["inputs"]:
                        edges.append(((inpts, process_name)))
                    for outpts in process_vars["outputs"]:
                        edges.append(((process_name, outpts)))
                c.attr(style='filled', color='lightgrey', label="12")
                c.node_attr.update(style='filled', color='white')
                c.edges(edges)

    def structs():
        """
        Examining structs using HTML like labels
            Pro:
                - Structures have boxes
                - Structure sub-items can have defined in/output ports
                - Looks more like I think it should. Also duplicate processes are possible!
            Cons:
                - Complicated to create from string
                - String creation is a little dirty

        Returns
        -------
        graphviz.Digraph() object

        CheatSheet
        -------

        """
        pos_counter = 0
        edges = []
        for process_id, [struct, process] in enumerate(HARDCODED_ES_STRUCTURE.items()):
            node_string = "{" + str(struct) + "|"
            process_names = [f"<f{port}> {process_name}" for port, [process_name, process_params] in
                             enumerate(process.items())]
            for port, [process_name, process_params] in enumerate(process.items()):
                for source, target in zip(process_params["inputs"], process_params["outputs"]):
                    # adding input nodes
                    s.node(name=source, pos=f"0,{pos_counter * 100}", tailport="e", headport="w")
                    # adding output nodes
                    s.node(name=target, pos=f"300,{pos_counter * 100}", tailport="e", headport="w")
                    edges.append((source, f"{struct}:<f{port}>:w"))
                    edges.append((f"{struct}:<f{port}>:e", target))

                    pos_counter += 0.5

            node_string += '|'.join(process_names)
            node_string += "}"
            print(node_string)
            s.node(str(struct), node_string, tailport="e", headport="w", pos=f"150, {pos_counter * 100}")
        s.edges(edges)

    structs()
    # s.node_attr(nodesep=0.5)
    # s.edges([('struct1:f1', 'struct2:f0'), ('struct1:f2', 'struct3:here')])
    return s


def main():
    draw_struct_graphviz(HARDCODED_ES_STRUCTURE=HARDCODED_ES_STRUCTURE, ADDITONAL_PARAMETERS=ADDITONAL_PARAMETERS).save(
        "test.dot")


if __name__ == "__main__":
    main()
