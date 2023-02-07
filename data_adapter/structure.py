from collections import defaultdict, namedtuple
from databus import download_collection

import os
import json


# download_collection(collection_url = "https://energy.databus.dbpedia.org/felixmaur/collections/modex_test_renewable")

class StructureError(Exception):
    """Raised if structure is corrupted"""



this_path = "../collections/hack-a-thon/"

with open(this_path + "HARDCODED_ES_STRUCT.json", "r") as f:
    HARDCODED_ES_STRUCTURE = json.read(f)


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


