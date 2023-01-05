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
