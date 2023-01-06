import networkx as nx
import jmespath
import matplotlib.pyplot as plt
from collections import defaultdict, namedtuple


class StructureError(Exception):
    """Raised if structure is corrupted"""


HARDCODED_ES_STRUCTURE = {
    "energy transformation unit": {
        "input_ratio": {"inputs": ["gas"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["gas"], "outputs": ["electricity"]},
        "emission_factor": {"inputs": ["gas"], "outputs": ["co2"]},
    },
    "battery storage": {
        "input_ratio": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "e2p_ratio": {"inputs": ["electricity"], "outputs": []},
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


def draw_struct(HARDCODED_ES_STRUCTURE: dict, ADDITONAL_PARAMETERS: dict)-> nx.Graph:
    """

    Parameters
    ----------
    HARDCODED_ES_STRUCTURE
    ADDITONAL_PARAMETERS

    Returns
    -------
    plottable Networkx Graph illustrating the Models structure given to the Frameworks

    """

    def ckeck_list_singular(lst)->bool:
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
    pos  = {}
    i = 0
    x = 0
    for unit, process in HARDCODED_ES_STRUCTURE.items():
        i = i+2
        pos[unit] = (1,i)
        k=0
        if ckeck_list_singular(jmespath.search("@.*.inputs[]", HARDCODED_ES_STRUCTURE[unit])) and\
                ckeck_list_singular(jmespath.search("@.*.outputs[]", HARDCODED_ES_STRUCTURE[unit])):

            for process_name, process_parameters in process.items():
                pos[process_name+unit] = (2,i+k)
                edges.append((unit, process_name+unit))
                edges.append((unit, process_parameters["inputs"][0]))
                edges.append((unit, process_parameters["outputs"][0]))
                break
        elif ckeck_list_singular(jmespath.search("@.*.inputs[]", HARDCODED_ES_STRUCTURE[unit])) and not\
                ckeck_list_singular(jmespath.search("@.*.outputs[]", HARDCODED_ES_STRUCTURE[unit])):
            for process_name, process_parameters in process.items():
                pos[process_name+unit] = (1,i+k)

                edges.append((unit, process_name+unit))
                edges.append((unit, process_parameters["inputs"][0]))
                edges.append((process_name+unit, process_parameters["outputs"][0]))
        else:
            for process_name, process_parameters in process.items():
                pos[process_name+unit] = (1,i+k)

                edges.append((unit, process_name))
                edges.append((process_name+unit, process_parameters["inputs"][0]))
                edges.append((process_name+unit, process_parameters["outputs"][0]))
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
    G.add_edges_from(edges)

    plt.figure(figsize=(6, 4))
    nx.draw_networkx(G, pos=pos)
    plt.show()

draw_struct(HARDCODED_ES_STRUCTURE=HARDCODED_ES_STRUCTURE, ADDITONAL_PARAMETERS=ADDITONAL_PARAMETERS)