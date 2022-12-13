def get_energy_structure():
    return {
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
        "onshore wind farm": {
            "installed_capacity": {
                "inputs": ["onshore wind farm"],
                "outputs": ["electricity"],
            }
        },
    }
