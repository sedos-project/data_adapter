from units import NamedComposedUnit, scaled_unit, unit
from units.exception import IncompatibleUnitsError
from units.predefined import define_units
from units.registry import REGISTRY


class UnitConversionError(Exception):
    """Raises when unit conversion goes wrong"""


def define_energy_model_units():
    unit("percent")
    unit("vehicle")

    scaled_unit("kW", "W", 1e3)
    scaled_unit("MW", "kW", 1e3)
    scaled_unit("GW", "MW", 1e3)
    scaled_unit("TW", "GW", 1e3)

    scaled_unit("min", "s", 60)
    scaled_unit("h", "min", 60)
    scaled_unit("day", "h", 24)
    scaled_unit("a", "day", 365)

    scaled_unit("t", "kg", 1e3)
    scaled_unit("kt", "t", 1e3)
    scaled_unit("Mt", "kt", 1e3)
    scaled_unit("Gt", "Mt", 1e3)

    scaled_unit("kp", "p", 1e3)
    scaled_unit("Mp", "kp", 1e3)
    scaled_unit("Gp", "Mp", 1e3)

    scaled_unit("100km", "km", 1e2)
    scaled_unit("Mm", "km", 1e3)
    scaled_unit("Gm", "Mm", 1e3)

    scaled_unit("kpkm", "pkm", 1e3)
    scaled_unit("Mpkm", "kpkm", 1e3)
    scaled_unit("Gpkm", "Mpkm", 1e3)

    scaled_unit("ktkm", "tkm", 1e3)
    scaled_unit("Mtkm", "ktkm", 1e3)
    scaled_unit("Gtkm", "Mtkm", 1e3)

    scaled_unit("tCO2eq", "kgCO2eq", 1e3)
    scaled_unit("ktCO2eq", "tCO2eq", 1e3)
    scaled_unit("MtCO2eq", "ktCO2eq", 1e3)
    scaled_unit("GtCO2eq", "MtCO2eq", 1e3)

    scaled_unit("kEUR", "EUR", 1e3)
    scaled_unit("MEUR", "kEUR", 1e3)
    scaled_unit("BEUR", "MEUR", 1e3)
    scaled_unit("TEUR", "BEUR", 1e3)

    scaled_unit("k_units", "units", 1e3)
    scaled_unit("M_units", "k_units", 1e3)
    scaled_unit("G_units", "M_units", 1e3)
    scaled_unit("T_units", "G_units", 1e3)

    scaled_unit("vehicles", "vehicle", 1)
    scaled_unit("number vehicles", "vehicles", 1)
    scaled_unit("kvehicles", "vehicles", 1e3)
    scaled_unit("Mvehicles", "kvehicles", 1e3)
    scaled_unit("Gvehicles", "Mvehicles", 1e3)
    scaled_unit("Tvehicles", "Gvehicles", 1e3)

    NamedComposedUnit("kWh", unit("kW") * unit("h"))
    NamedComposedUnit("MWh", unit("MW") * unit("h"))
    NamedComposedUnit("GWh", unit("GW") * unit("h"))
    NamedComposedUnit("TWh", unit("TW") * unit("h"))

    NamedComposedUnit("MWh*a", unit("MWh") * unit("a"))
    NamedComposedUnit("Mt*a", unit("Mt") * unit("a"))
    NamedComposedUnit("vehicle*a", unit("vehicle") * unit("a"))

    NamedComposedUnit("kW/h", unit("kW") / unit("h"))
    NamedComposedUnit("MW/h", unit("MW") / unit("h"))
    NamedComposedUnit("GW/h", unit("GW") / unit("h"))
    NamedComposedUnit("TW/h", unit("TW") / unit("h"))

    NamedComposedUnit("MWh/MWh", unit("MWh") / unit("MWh"))
    NamedComposedUnit("MWh/MW", unit("MWh") / unit("MW"))
    NamedComposedUnit("MWh/t", unit("MWh") / unit("t"))
    NamedComposedUnit("MWh/M_units", unit("MWh") / unit("M_units"))

    NamedComposedUnit("EUR/t", unit("EUR") / unit("t"))
    NamedComposedUnit("MEUR/Mt", unit("MEUR") / unit("Mt"))
    NamedComposedUnit("EUR/Mt", unit("EUR") / unit("Mt"))

    NamedComposedUnit("EUR/MWh", unit("EUR") / unit("MWh"))

    NamedComposedUnit("EUR/(MWh*a)", unit("EUR") / unit("MWh*a"))
    NamedComposedUnit("MEUR/(Mt*a)", unit("MEUR") / unit("Mt*a"))
    NamedComposedUnit("EUR/(vehicle*a)", unit("EUR") / unit("vehicle*a"))

    NamedComposedUnit("EUR/vehicle", unit("EUR") / unit("vehicle"))

    NamedComposedUnit("kWh/100km", unit("kWh") / unit("100km"))

    NamedComposedUnit("kg/MWh", unit("kg") / unit("MWh"))
    NamedComposedUnit("kg/t", unit("kg") / unit("t"))

    NamedComposedUnit("km/a", unit("km") / unit("a"))

    NamedComposedUnit("percent/h", unit("percent") / unit("h"))
    NamedComposedUnit("p/vehicle", unit("p") / unit("vehicle"))
    NamedComposedUnit("t/vehicle", unit("t") / unit("vehicle"))


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
