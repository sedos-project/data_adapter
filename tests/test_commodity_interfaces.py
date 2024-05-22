import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from  data_adapter.preprocessing import Structure



structure = Structure(
    "SEDOS_Modellstruktur",
    process_sheet="Processes_O1",
    parameter_sheet="Parameter_O1",
    helper_sheet="Helper_O1",
)

structure.plot_commodity_interfaces()

print(structure.get_commodity_diff())

