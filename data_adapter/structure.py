from collections import defaultdict, namedtuple

import graphviz
import jmespath
import networkx as nx


class StructureError(Exception):
    """Raised if structure is corrupted"""


HARDCODED_ES_STRUCTURE = {
    "gasturbine": {
        "input_ratio": {"inputs": ["gas"], "outputs": ["output_ratio"]},
        "output_ratio": {"inputs": ["input_ratio"], "outputs": ["electricity"]},
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


def draw_struct(HARDCODED_ES_STRUCTURE: dict, ADDITONAL_PARAMETERS: dict) -> nx.Graph:
    """

    Parameters
    ----------
    HARDCODED_ES_STRUCTURE
    ADDITONAL_PARAMETERS

    Returns
    -------
    plottable Networkx Graph illustrating the Models structure given to the Frameworks

    """

    def ckeck_list_singular(lst) -> bool:
        ele = lst[0]
        chk = True
        # Comparing each element with first item
        for item in lst:
            if ele != item:
                chk = False
                break
        return chk

    # Empty Graph:
    G = nx.DiGraph()
    edges = []
    pos = {}
    i = 0
    x = 0
    for unit, process in HARDCODED_ES_STRUCTURE.items():
        i = i + 2
        pos[unit] = (1, i)
        k = 0
        if ckeck_list_singular(jmespath.search("@.*.inputs[]", HARDCODED_ES_STRUCTURE[unit])) and \
                ckeck_list_singular(jmespath.search("@.*.outputs[]", HARDCODED_ES_STRUCTURE[unit])):

            for process_name, process_parameters in process.items():
                pos[process_name + unit] = (2, i + k)
                edges.append((unit, process_name + unit))
                edges.append((unit, process_parameters["inputs"][0]))
                edges.append((unit, process_parameters["outputs"][0]))
                break
        elif ckeck_list_singular(jmespath.search("@.*.inputs[]", HARDCODED_ES_STRUCTURE[unit])) and not \
                ckeck_list_singular(jmespath.search("@.*.outputs[]", HARDCODED_ES_STRUCTURE[unit])):
            for process_name, process_parameters in process.items():
                pos[process_name + unit] = (1, i + k)

                edges.append((unit, process_name + unit))
                edges.append((unit, process_parameters["inputs"][0]))
                edges.append((process_name + unit, process_parameters["outputs"][0]))
        else:
            for process_name, process_parameters in process.items():
                pos[process_name + unit] = (1, i + k)

                edges.append((unit, process_name))
                edges.append((process_name + unit, process_parameters["inputs"][0]))
                edges.append((process_name + unit, process_parameters["outputs"][0]))
    print(jmespath.search("*.*.inputs[][]", HARDCODED_ES_STRUCTURE))
    for y, inpt in enumerate(jmespath.search("*.*.inputs[][]", HARDCODED_ES_STRUCTURE)):
        if inpt in pos:
            pass
        else:
            pos[inpt] = (0, y)
    for y, opt in enumerate(jmespath.search("*.*.outputs[][]", HARDCODED_ES_STRUCTURE)):
        if opt in pos:
            pass
        else:
            pos[opt] = (3, y)

    print(edges)
    print(pos)


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

        edges = []
        for struct, process in HARDCODED_ES_STRUCTURE.items():
            node_string = "{" + str(struct) + "|"
            process_names = [f"<f{port}> {process_name}" for port, [process_name, process_params] in
                             enumerate(process.items())]
            for port, [process_name, process_params] in enumerate(process.items()):
                [edges.append((target, f"{struct}:<f{port}>:w")) for target in process_params["inputs"]]
                [edges.append((f"{struct}:<f{port}>:e", target)) for target in process_params["outputs"]]
            node_string += '|'.join(process_names)
            node_string += "}"
            s.node(str(struct), node_string, tailport="e", headport="w")
        s.edges(edges)

    structs()
    # s.node_attr(nodesep=0.5)
    # s.edges([('struct1:f1', 'struct2:f0'), ('struct1:f2', 'struct3:here')])
    return s


draw_struct_graphviz(HARDCODED_ES_STRUCTURE=HARDCODED_ES_STRUCTURE, ADDITONAL_PARAMETERS=ADDITONAL_PARAMETERS).save(
    "test.dot")
