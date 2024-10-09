from units import NamedComposedUnit, scaled_unit, unit
from units.exception import IncompatibleUnitsError
from units.predefined import define_units
from units.registry import REGISTRY


class UnitConversionError(Exception):
    """Raises when unit conversion goes wrong"""


def define_energy_model_units():
    # These units are not defined:
    # PJ, Mt, [0,1], pkm or tkm or kWh,


    unit('t_CO2')
    unit('TJ_input')
    scaled_unit('kg_CH4','t_CO2', 0.025)  # maybe wrong
    scaled_unit('kg_N2O','t_CO2', 0.298)  # maybe wrong
    NamedComposedUnit("kg_CH4/TJ_input", unit("kg_CH4") / unit("TJ_input"))
    NamedComposedUnit("kg_N2O/TJ_input", unit("kg_N2O") / unit("TJ_input"))
    NamedComposedUnit("t_CO2/TJ_input", unit("t_CO2") / unit("TJ_input"))

    scaled_unit("%", "percent", 1)

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
    scaled_unit("M€", "MEUR", 1)

    scaled_unit("k_units", "units", 1e3)
    scaled_unit("M_units", "k_units", 1e3)
    scaled_unit("G_units", "M_units", 1e3)
    scaled_unit("T_units", "G_units", 1e3)
    scaled_unit("Million units", "M_units", 1)

    scaled_unit("vehicles", "vehicle", 1)
    scaled_unit("number vehicles", "vehicles", 1)
    scaled_unit("kvehicles", "vehicles", 1e3)
    scaled_unit("Mvehicles", "kvehicles", 1e3)
    scaled_unit("Gvehicles", "Mvehicles", 1e3)
    scaled_unit("Tvehicles", "Gvehicles", 1e3)



    NamedComposedUnit("Wh", unit("W") * unit("h"))
    NamedComposedUnit("kWh", unit("kW") * unit("h"))
    NamedComposedUnit("MWh", unit("MW") * unit("h"))
    NamedComposedUnit("GWh", unit("GW") * unit("h"))
    NamedComposedUnit("TWh", unit("TW") * unit("h"))

    NamedComposedUnit("kWh*day", unit("kWh") * unit("day"))
    NamedComposedUnit("MWh*day", unit("MWh") * unit("day"))
    NamedComposedUnit("GWh*day", unit("GWh") * unit("day"))
    NamedComposedUnit("kWh*a", unit("kWh") * unit("a"))
    NamedComposedUnit("MWh*a", unit("MWh") * unit("a"))
    NamedComposedUnit("GWh*a", unit("GWh") * unit("a"))
    NamedComposedUnit("t*a", unit("t") * unit("a"))
    NamedComposedUnit("t*day", unit("t") * unit("day"))
    NamedComposedUnit("kt*day", unit("kt") * unit("day"))
    NamedComposedUnit("Mt*day", unit("Mt") * unit("day"))
    NamedComposedUnit("Gt*day", unit("Gt") * unit("day"))
    NamedComposedUnit("kt*a", unit("kt") * unit("a"))
    NamedComposedUnit("Mt*a", unit("Mt") * unit("a"))
    NamedComposedUnit("Gt*a", unit("Gt") * unit("a"))
    NamedComposedUnit("vehicle*a", unit("vehicle") * unit("a"))
    NamedComposedUnit("vehicle*day", unit("vehicle") * unit("day"))

    NamedComposedUnit("kW/h", unit("kW") / unit("h"))
    NamedComposedUnit("MW/h", unit("MW") / unit("h"))
    NamedComposedUnit("GW/h", unit("GW") / unit("h"))
    NamedComposedUnit("TW/h", unit("TW") / unit("h"))

    NamedComposedUnit("MWh/MWh", unit("MWh") / unit("MWh"))
    NamedComposedUnit("MWh/MW", unit("MWh") / unit("MW"))
    NamedComposedUnit("MWh/t", unit("MWh") / unit("t"))
    NamedComposedUnit("MWh/kt", unit("MWh") / unit("kt"))
    NamedComposedUnit("MWh/k_units", unit("MWh") / unit("k_units"))
    NamedComposedUnit("MWh/M_units", unit("MWh") / unit("M_units"))
    NamedComposedUnit("MWh/G_units", unit("MWh") / unit("G_units"))

    # ------ EUR/**  ------
    NamedComposedUnit("EUR/t", unit("EUR") / unit("t"))
    NamedComposedUnit("€/t", unit("EUR") / unit("t"))
    NamedComposedUnit("kEUR/t", unit("kEUR") / unit("t"))
    NamedComposedUnit("MEUR/t", unit("MEUR") / unit("t"))
    NamedComposedUnit("BEUR/t", unit("BEUR") / unit("t"))
   
    NamedComposedUnit("EUR/Mt", unit("EUR") / unit("Mt"))
    NamedComposedUnit("kEUR/Mt", unit("kEUR") / unit("Mt"))
    NamedComposedUnit("MEUR/Mt", unit("MEUR") / unit("Mt"))
    NamedComposedUnit("BEUR/Mt", unit("BEUR") / unit("Mt"))

    NamedComposedUnit("EUR/kWh", unit("EUR") / unit("kWh"))
    NamedComposedUnit("EUR/MWh", unit("EUR") / unit("MWh"))
    NamedComposedUnit("€/MWh", unit("EUR") / unit("MWh"))
    NamedComposedUnit("€/MWj", unit("€") / unit("MWj")) # how to define MWj?

    NamedComposedUnit("kEUR/MWh", unit("kEUR") / unit("MWh"))
    NamedComposedUnit("MEUR/MWh", unit("MEUR") / unit("MWh"))

    NamedComposedUnit("EUR/(MWh*a)", unit("EUR") / unit("MWh*a"))
    NamedComposedUnit("kEUR/(MWh*a)", unit("kEUR") / unit("MWh*a"))
    NamedComposedUnit("MEUR/(MWh*a)", unit("MEUR") / unit("MWh*a"))

    NamedComposedUnit("EUR/(Mt*a)", unit("EUR") / unit("Mt*a"))
    NamedComposedUnit("kEUR/(Mt*a)", unit("kEUR") / unit("Mt*a"))
    NamedComposedUnit("MEUR/(Mt*a)", unit("MEUR") / unit("Mt*a"))

    NamedComposedUnit("EUR/(vehicle*a)", unit("EUR") / unit("vehicle*a"))
    NamedComposedUnit("kEUR/(vehicle*a)", unit("kEUR") / unit("vehicle*a"))
    NamedComposedUnit("MEUR/(vehicle*a)", unit("MEUR") / unit("vehicle*a"))

    NamedComposedUnit("EUR/MW", unit("EUR") / unit("MW"))
    NamedComposedUnit("€/MW", unit("EUR") / unit("MW"))

    NamedComposedUnit("EUR/MW*a", unit("EUR") / unit("MW") * unit("a"))
    NamedComposedUnit("€/MW*a", unit("EUR") / unit("MW") * unit("a"))
    NamedComposedUnit("EUR/MW/a", unit("EUR") / unit("MW") / unit("a"))

    NamedComposedUnit("EUR/vehicle", unit("EUR") / unit("vehicle"))
    NamedComposedUnit("kEUR/vehicle", unit("kEUR") / unit("vehicle"))
    NamedComposedUnit("MEUR/vehicle", unit("MEUR") / unit("vehicle"))

    NamedComposedUnit("EUR/kW", unit("EUR") / unit("kW"))
    NamedComposedUnit("EUR/kW*a,", unit("EUR") / unit("kW") * unit("a"))

    NamedComposedUnit("EUR/pkm", unit("EUR") / unit("pkm"))
    NamedComposedUnit("M€/GW", unit("MEUR") / unit("GW"))
    NamedComposedUnit("M€/Kt CO2-eq", unit("MEUR") / unit("Kt")) # whats the difference of Kt and  kt
    NamedComposedUnit("M€/Million units", unit("MEUR") / unit("M_units"))
    NamedComposedUnit("M€/Million units", unit("MEUR") / unit("PJ"))

    NamedComposedUnit("kWh/100km", unit("kWh") / unit("100km"))
    NamedComposedUnit("MWh/100km", unit("MWh") / unit("100km"))

    NamedComposedUnit("kg/MWh", unit("kg") / unit("MWh"))
    NamedComposedUnit("kg/kWh", unit("kg") / unit("kWh"))
    NamedComposedUnit("kg/t", unit("kg") / unit("t"))

    NamedComposedUnit("km/a", unit("km") / unit("a"))
    NamedComposedUnit("km/day", unit("km") / unit("day"))
    NamedComposedUnit("Mm/a", unit("Mm") / unit("a"))

    NamedComposedUnit("percent/h", unit("percent") / unit("h"))
    NamedComposedUnit("percent/day", unit("percent") / unit("day"))
    NamedComposedUnit("percent/a", unit("percent") / unit("a"))
    NamedComposedUnit("percent/vehicle", unit("percent") / unit("vehicle"))

    NamedComposedUnit("p/vehicle", unit("p") / unit("vehicle"))
    NamedComposedUnit("kp/vehicle", unit("kp") / unit("vehicle"))
    NamedComposedUnit("Mp/vehicle", unit("Mp") / unit("vehicle"))
    NamedComposedUnit("t/vehicle", unit("t") / unit("vehicle"))
    NamedComposedUnit("kg/vehicle", unit("kg") / unit("vehicle"))

    NamedComposedUnit("%/h", unit("%") / unit("h"))

    NamedComposedUnit("Million units/Million units", unit("M_units") / unit("M_units"))
    NamedComposedUnit("Kt/Million units", unit("Kt") / unit("Million units"))

    # how to define Kt， Mt，PJ？
    NamedComposedUnit("Kt/Kt", unit("Kt") / unit("Kt"))
    NamedComposedUnit("Kt/Mt", unit("Kt") / unit("Mt"))
    NamedComposedUnit("Kt/PJ", unit("Kt") / unit("PJ"))
    NamedComposedUnit("Mt/Mt", unit("Mt") / unit("Mt"))
    NamedComposedUnit("Mt/PJ", unit("Mt") / unit("PJ"))

    NamedComposedUnit("kt/Kt", unit("kt")/unit("Kt"))
    NamedComposedUnit("kt/Mt", unit("kt")/unit("Mt"))

    NamedComposedUnit("PJ/Million units", unit("PJ") / unit("M_units"))
    NamedComposedUnit("PJ/Mt", unit("PJ") / unit("Mt"))
    NamedComposedUnit("PJ/PJ", unit("PJ") / unit("PJ"))

    NamedComposedUnit("kW/kW", unit("kW") / unit("kW"))
    NamedComposedUnit("kWh/kWh", unit("kWh") / unit("kWh"))

    NamedComposedUnit("kWh/100km", unit("kWh") / unit("100km"))
    NamedComposedUnit("kWh/km", unit("kWh") / unit("km"))

    NamedComposedUnit("kW/a", unit("kW") / unit("a"))

    NamedComposedUnit("t/t", unit("t") / unit("t"))
    NamedComposedUnit("t/MWh", unit("t") / unit("MWh"))


    # how to define [0,1]？



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
