from units import NamedComposedUnit, scaled_unit, unit
from units.exception import IncompatibleUnitsError
from units.predefined import define_units
from units.registry import REGISTRY


class UnitConversionError(Exception):
    """Raises when unit conversion goes wrong"""


def define_energy_model_units():
    scaled_unit("kW", "W", 1e3)
    scaled_unit("MW", "kW", 1e3)
    scaled_unit("GW", "MW", 1e3)
    scaled_unit("TW", "GW", 1e3)

    scaled_unit("a", "day", 365)

    scaled_unit("kt", "t", 1e3)
    scaled_unit("Mt", "kt", 1e3)
    scaled_unit("Gt", "Mt", 1e3)

    NamedComposedUnit("kWh", unit("kW") * unit("h"))
    NamedComposedUnit("MWh", unit("MW") * unit("h"))
    NamedComposedUnit("GWh", unit("GW") * unit("h"))
    NamedComposedUnit("TWh", unit("TW") * unit("h"))

    NamedComposedUnit("kW/h", unit("kW") / unit("h"))
    NamedComposedUnit("MW/h", unit("MW") / unit("h"))
    NamedComposedUnit("GW/h", unit("GW") / unit("h"))
    NamedComposedUnit("TW/h", unit("TW") / unit("h"))


define_units()
define_energy_model_units()


def get_conversion_factor(convert_from, convert_to):
    if convert_from not in REGISTRY:
        raise UnitConversionError(f"Unknown unit '{convert_from}'.")
    if convert_to not in REGISTRY:
        raise UnitConversionError(f"Unknown unit '{convert_to}'.")
    try:
        return unit(convert_to)(unit(convert_from)(1)).get_num()
    except IncompatibleUnitsError:
        raise IncompatibleUnitsError(f"Cannot convert from unit '{convert_from}' to unit '{convert_to}'")
