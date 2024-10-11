from data_adapter import unit_conversion
from pytest import approx

def test_unit_conversion():

    assert unit_conversion.get_conversion_factor("Gp", "p") == 1e9
    assert unit_conversion.get_conversion_factor("Mp", "p") == 1e6
    assert unit_conversion.get_conversion_factor("Gp", "kp") == 1e6

    # Test power units
    assert unit_conversion.get_conversion_factor("GW", "W") == 1e9
    assert unit_conversion.get_conversion_factor("TW", "kW") == 1e9
    assert unit_conversion.get_conversion_factor("MW", "W") == 1e6
    assert unit_conversion.get_conversion_factor("kW", "W") == 1e3
    assert unit_conversion.get_conversion_factor("MW", "kW") == 1e3
    assert unit_conversion.get_conversion_factor("GW", "MW") == 1e3
    assert unit_conversion.get_conversion_factor("TW", "GW") == 1e3

    # Test time units
    assert unit_conversion.get_conversion_factor("a", "min") == 365 * 24 * 60
    assert unit_conversion.get_conversion_factor("h", "s") == 60 * 60
    assert unit_conversion.get_conversion_factor("min", "s") == 60
    assert unit_conversion.get_conversion_factor("h", "min") == 60
    assert unit_conversion.get_conversion_factor("day", "h") == 24
    assert unit_conversion.get_conversion_factor("a", "day") == 365
    assert unit_conversion.get_conversion_factor("day", "min") == 24 * 60

    # Test mass units
    assert unit_conversion.get_conversion_factor("t", "kg") == 1e3
    assert unit_conversion.get_conversion_factor("Mt", "t") == 1e6
    assert unit_conversion.get_conversion_factor("Gt", "kt") == 1e6
    assert unit_conversion.get_conversion_factor("Mt", "kg") == 1e9
    assert unit_conversion.get_conversion_factor("Gt", "kg") == 1e12
    assert unit_conversion.get_conversion_factor("Gt", "t") == 1e9
    assert unit_conversion.get_conversion_factor("kg", "Mt") == 1 / 1e9
    assert unit_conversion.get_conversion_factor("kg", "Gt") == 1 / 1e12

    # Test monetary units
    assert unit_conversion.get_conversion_factor("kEUR", "EUR") == 1e3
    assert unit_conversion.get_conversion_factor("MEUR", "EUR") == 1e6
    assert unit_conversion.get_conversion_factor("BEUR", "EUR") == 1e9
    assert unit_conversion.get_conversion_factor("TEUR", "EUR") == 1e12
    assert unit_conversion.get_conversion_factor("TEUR", "MEUR") == 1e6
    assert unit_conversion.get_conversion_factor("BEUR", "kEUR") == 1e6
    assert unit_conversion.get_conversion_factor("M€", "MEUR") == 1
    assert unit_conversion.get_conversion_factor("M€", "EUR") == 1e6

    # Test monetary-related units
    assert unit_conversion.get_conversion_factor("kEUR/t", "EUR/t") == approx(1e3)
    assert unit_conversion.get_conversion_factor("MEUR/t", "kEUR/t") == 1e3
    assert unit_conversion.get_conversion_factor("BEUR/t", "EUR/t") == 1e9
    assert unit_conversion.get_conversion_factor("kEUR/Mt", "EUR/Mt") == approx(1e3)
    assert unit_conversion.get_conversion_factor("BEUR/Mt", "EUR/Mt") == 1e9
    assert unit_conversion.get_conversion_factor("MEUR/Mt", "kEUR/Mt") == approx(1e3)
    assert unit_conversion.get_conversion_factor("BEUR/Mt", "MEUR/Mt") == approx(1e3)
    assert unit_conversion.get_conversion_factor("EUR/kWh", "EUR/MWh") == approx(1e3)
    assert unit_conversion.get_conversion_factor("kEUR/MWh", "EUR/MWh") == approx(1e3)
    assert unit_conversion.get_conversion_factor("MEUR/MWh", "kEUR/MWh") == 1e3
    assert unit_conversion.get_conversion_factor("MEUR/MWh", "EUR/MWh") == approx(1e6)
    assert unit_conversion.get_conversion_factor("MEUR/(MWh*a)", "EUR/(MWh*a)") == approx(1e6)
    assert unit_conversion.get_conversion_factor("MEUR/(MWh*a)", "kEUR/(MWh*a)") == approx(1e3)
    assert unit_conversion.get_conversion_factor("MEUR/(Mt*a)", "EUR/(Mt*a)") == 1e6
    assert unit_conversion.get_conversion_factor("MEUR/(Mt*a)", "kEUR/(Mt*a)") == approx(1e3)
    assert unit_conversion.get_conversion_factor("MEUR/(vehicle*a)", "EUR/(vehicle*a)") == 1e6
    assert unit_conversion.get_conversion_factor("MEUR/(vehicle*a)", "kEUR/(vehicle*a)") == 1e3
    assert unit_conversion.get_conversion_factor("MEUR/vehicle", "EUR/vehicle") == 1e6
    assert unit_conversion.get_conversion_factor("MEUR/vehicle", "kEUR/vehicle") == 1e3
    assert unit_conversion.get_conversion_factor("kEUR/t", "€/t") == approx(1e3)
    assert unit_conversion.get_conversion_factor("EUR/t", "€/t") == 1
    assert unit_conversion.get_conversion_factor("€/MWh", "EUR/MWh") == 1
    assert unit_conversion.get_conversion_factor("EUR/W", "EUR/MW") == 1e6
    assert unit_conversion.get_conversion_factor("EUR/W", "€/MW") == 1e6
    assert unit_conversion.get_conversion_factor("EUR/MW", "€/MW") == 1
    assert unit_conversion.get_conversion_factor("EUR/MW*a", "€/MW*a") == 1
    assert unit_conversion.get_conversion_factor("EUR/W", "EUR/kW") ==approx(1e3)
    assert unit_conversion.get_conversion_factor("EUR/pkm", "EUR/kpkm") ==approx(1e3)
    assert unit_conversion.get_conversion_factor("MEUR/GW", "M€/GW") ==1
    assert unit_conversion.get_conversion_factor("MEUR/Kt CO2-eq", "M€/Kt CO2-eq") ==1
    assert unit_conversion.get_conversion_factor("MEUR/Million units", "M€/Million units") ==1
    assert unit_conversion.get_conversion_factor("MEUR/PJ", "M€/PJ") ==1
    
    # Test distance units
    assert unit_conversion.get_conversion_factor("100km", "km") == 1e2
    assert unit_conversion.get_conversion_factor("Gm", "km") == 1e6
    assert unit_conversion.get_conversion_factor("Mm", "km") == 1e3
    assert unit_conversion.get_conversion_factor("Mm", "100km") == 1e1
    assert unit_conversion.get_conversion_factor("kWh/km", "kWh/100km") == 1e2


    # Test units units
    assert unit_conversion.get_conversion_factor("T_units", "units") == 1e12
    assert unit_conversion.get_conversion_factor("G_units", "k_units") == 1e6
    assert unit_conversion.get_conversion_factor("G_units", "M_units") == 1e3
    assert unit_conversion.get_conversion_factor("T_units", "M_units") == 1e6
    assert unit_conversion.get_conversion_factor("T_units", "G_units") == 1e3
    assert unit_conversion.get_conversion_factor("Million units", "M_units") == 1
    assert unit_conversion.get_conversion_factor("G_units", "Million units") == 1e3
    assert unit_conversion.get_conversion_factor("Kt/Million units", "Kt/M_units") == 1

    # Test vehicle units
    assert unit_conversion.get_conversion_factor("vehicles", "vehicle") == 1
    assert unit_conversion.get_conversion_factor("number vehicles", "vehicle") == 1
    assert unit_conversion.get_conversion_factor("vehicles", "kvehicles") == 1 / 1e3
    assert unit_conversion.get_conversion_factor("kvehicles", "vehicles") == 1e3
    assert unit_conversion.get_conversion_factor("Mvehicles", "vehicles") == 1e6
    assert unit_conversion.get_conversion_factor("Gvehicles", "kvehicles") == 1e6
    assert unit_conversion.get_conversion_factor("Tvehicles", "vehicles") == 1e12
    assert unit_conversion.get_conversion_factor("percent/vehicle", "percent/kvehicles") == 1e3
    
    # Test CO2 equivalent units
    assert unit_conversion.get_conversion_factor("tCO2eq", "kgCO2eq") == 1e3
    assert unit_conversion.get_conversion_factor("ktCO2eq", "kgCO2eq") == 1e6
    assert unit_conversion.get_conversion_factor("MtCO2eq", "kgCO2eq") == 1e9
    assert unit_conversion.get_conversion_factor("GtCO2eq", "tCO2eq") == 1e9
    assert unit_conversion.get_conversion_factor("MtCO2eq", "tCO2eq") == 1e6

    # Test pkm and tkm units
    assert unit_conversion.get_conversion_factor("Gpkm", "kpkm") == 1e6
    assert unit_conversion.get_conversion_factor("Mpkm", "pkm") == 1e6
    assert unit_conversion.get_conversion_factor("Gpkm", "pkm") == 1e9
    assert unit_conversion.get_conversion_factor("Gtkm", "ktkm") == 1e6
    assert unit_conversion.get_conversion_factor("Mtkm", "tkm") == 1e6
    assert unit_conversion.get_conversion_factor("Gtkm", "tkm") == 1e9

    # Test energy units
    assert unit_conversion.get_conversion_factor("GWh", "Wh") == 1e9
    assert unit_conversion.get_conversion_factor("MWh", "Wh") == 1e6
    assert unit_conversion.get_conversion_factor("GWh", "kWh") == 1e6
    assert unit_conversion.get_conversion_factor("TWh", "kWh") == 1e9

    # Test composed energy-time units
    assert unit_conversion.get_conversion_factor("MWh*a", "MWh*day") == 365
    assert unit_conversion.get_conversion_factor("MWh*day", "kWh*day") == 1e3
    assert unit_conversion.get_conversion_factor("GWh*day", "kWh*day") == 1e6
    assert unit_conversion.get_conversion_factor("GWh*day", "MWh*day") == 1e3
    assert unit_conversion.get_conversion_factor("GWh*a", "kWh*a") == approx(1e6)
    assert unit_conversion.get_conversion_factor("GWh*a", "MWh*a") == approx(1e3)

    # Test composed mass-time units
    assert unit_conversion.get_conversion_factor("Mt*a", "Mt*day") == 365
    assert unit_conversion.get_conversion_factor("Mt*day", "kt*day") == 1e3
    assert unit_conversion.get_conversion_factor("Gt*day", "kt*day") == 1e6
    assert unit_conversion.get_conversion_factor("Gt*day", "t*day") == 1e9
    assert unit_conversion.get_conversion_factor("Mt*a", "kt*a") == 1e3
    assert unit_conversion.get_conversion_factor("Gt*a", "t*a") == 1e9

    # Test energy rate units
    assert unit_conversion.get_conversion_factor("MW/h", "kW/h") == approx(1e3)
    assert unit_conversion.get_conversion_factor("GW/h", "MW/h") == approx(1e3)
    assert unit_conversion.get_conversion_factor("TW/h", "GW/h") == approx(1e3)
    assert unit_conversion.get_conversion_factor("TW/h", "kW/h") == approx(1e9)

    # Additional complex unit conversions
    assert unit_conversion.get_conversion_factor("kg", "Mt") == 1 / 1e9
    assert unit_conversion.get_conversion_factor("Mt", "Gt") == 1 / 1e3
    assert unit_conversion.get_conversion_factor("kEUR", "TEUR") == 1 / 1e9
    assert unit_conversion.get_conversion_factor("EUR", "BEUR") == 1 / 1e9

    # Test other units
    assert unit_conversion.get_conversion_factor("vehicle*a", "vehicle*day") == 365
    assert unit_conversion.get_conversion_factor("MWh/MW", "MWh/MW") == 1
    assert unit_conversion.get_conversion_factor("MWh/t", "MWh/kt") == 1e3
    assert unit_conversion.get_conversion_factor("MWh/M_units", "MWh/k_units") == 1 / 1e3
    assert unit_conversion.get_conversion_factor("MWh/G_units", "MWh/k_units") == 1 / 1e6
    assert unit_conversion.get_conversion_factor("MWh/100km", "kWh/100km") == 1e3
    assert unit_conversion.get_conversion_factor("kg/kWh", "kg/MWh") == 1e3
    assert unit_conversion.get_conversion_factor("Mm/a", "km/a") == 1e3
    assert unit_conversion.get_conversion_factor("km/day", "km/a") == 365
    assert unit_conversion.get_conversion_factor("t/MWh", "kg/MWh") == 1e3
    assert unit_conversion.get_conversion_factor("kW/a", "W/a") == 1e3
    
    assert unit_conversion.get_conversion_factor("percent/h", "percent/day") == 24
    assert unit_conversion.get_conversion_factor("percent/day", "percent/a") == 365
    assert unit_conversion.get_conversion_factor("percent/h", "percent/a") == 365 * 24
    assert unit_conversion.get_conversion_factor("kp/vehicle", "p/vehicle") == 1e3
    assert unit_conversion.get_conversion_factor("Mp/vehicle", "kp/vehicle") == 1e3
    assert unit_conversion.get_conversion_factor("Mp/vehicle", "p/vehicle") == 1e6
    assert unit_conversion.get_conversion_factor("t/vehicle", "kg/vehicle") == 1e3
    assert unit_conversion.get_conversion_factor("%", "percent") == 1
    assert unit_conversion.get_conversion_factor("%/h", "percent/h") == 1

    assert unit_conversion.get_conversion_factor("EUR/W/a","EUR/MW/a")== 1e6

    assert unit_conversion.get_conversion_factor("PJ","J")== 1e15
    assert unit_conversion.get_conversion_factor("kWh","PJ")== 3.6e-9

    assert unit_conversion.get_conversion_factor("Kt/PJ","kt/PJ")== 1
    assert unit_conversion.get_conversion_factor("Mt/PJ","Mt/PJ")== 1
    assert unit_conversion.get_conversion_factor("PJ/Million units","PJ/M_units")== 1
    assert unit_conversion.get_conversion_factor("PJ/Mt","PJ/Mt")== 1
    assert unit_conversion.get_conversion_factor("PJ/PJ","PJ/PJ")== 1
