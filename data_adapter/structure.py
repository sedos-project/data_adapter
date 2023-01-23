from collections import defaultdict, namedtuple

import graphviz
import jmespath
import networkx as nx


class StructureError(Exception):
    """Raised if structure is corrupted"""


HARDCODED_ES_STRUCTURE = {
    "many_inputs_outputs": {
        "input_ratio": {"inputs": ["lignite", "coal"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["lignite", "coal"], "outputs": ["electricity", "heat"]},
        "emission_factor": {"inputs": ["lignite", "coal"], "outputs": ["co2", "co", "so2"]},
        "price_timeseries": {"inputs": ["lignite", "coal"], "outputs": ["€", "$"]},
    },
    "gasturbine": {
        "input_ratio": {"inputs": ["gas"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["gas"], "outputs": ["electricity"]},
        "emission_factor": {"inputs": ["gas"], "outputs": ["co2"]},
    },
    "battery storage": {
        "input_ratio": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "e2p_ratio": {"inputs": ["electricity"], "outputs": []},
    },
    "Windpark": {
        "input_ratio": {"inputs": ["wind"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["wind"], "outputs": ["electricity"]},
    },
    "steam power": {
        "input_ratio": {"inputs": ["lignite"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["lignite"], "outputs": ["electricity"]},
        "emission_factor": {"inputs": ["lignite"], "outputs": ["co2"]},
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
        Trying to work with clusters
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
        Trying to work with clusters using HTML like labels
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


draw_struct_graphviz(HARDCODED_ES_STRUCTURE=HARDCODED_ES_STRUCTURE, ADDITONAL_PARAMETERS=ADDITONAL_PARAMETERS).save(
    "test.dot")
