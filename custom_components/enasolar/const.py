#! /usr/bin/env python3
"""Constants for the EnaSolar Integration."""

from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfTime,
    UnitOfIrradiance,
    PERCENTAGE,
)

DOMAIN = "enasolar"

DEFAULT_HOST = "my.inverter.fqdn"
DEFAULT_NAME = ""

CONF_HOST = "host"
CONF_NAME = "name"
CONF_NO_SUN = "no_sun"
CONF_CAPABILITY = "capability"
CONF_MAX_OUTPUT = "max_output"
CONF_DC_STRINGS = "dc_strings"

ENASOLAR = "enasolar"
SCAN_METERS_INTERVAL = 60

MAX_OUTPUT = (1.5, 2.0, 3.0, 3.8, 4.0, 5.0)
DC_STRINGS = (1, 2)

HAS_POWER_METER = 1
HAS_SOLAR_METER = 2
HAS_TEMPERATURE = 4
USE_FAHRENHIET = 256

ENASOLAR_UNIT_MAPPINGS = {
    "": None,
    "d": UnitOfTime.DAYS,
    "h": UnitOfTime.HOURS,
    "kW": UnitOfPower.KILO_WATT,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "V": UnitOfElectricPotential.VOLT,
    "kWh/m2": "kWh/m2",
    "W/m2": UnitOfIrradiance.WATTS_PER_SQUARE_METER,
    "C": UnitOfTemperature.CELSIUS,
    "F": UnitOfTemperature.FAHRENHEIT,
    "%": PERCENTAGE,
}
