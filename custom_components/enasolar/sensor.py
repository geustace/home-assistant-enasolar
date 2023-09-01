"""EnaSolar solar inverter interface."""

from __future__ import annotations
from datetime import date
import logging

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.sun import is_up
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import (
    CONF_CAPABILITY,
    CONF_DC_STRINGS,
    CONF_MAX_OUTPUT,
    DOMAIN,
    ENASOLAR_UNIT_MAPPINGS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Add enasolar entry."""

    # Use all sensors by default, but split them to have two update frequencies
    hass_meter_sensors = []
    hass_data_sensors = []

    enasolar = hass.data[DOMAIN][config_entry.entry_id]

    enasolar.capability = config_entry.data[CONF_CAPABILITY]
    enasolar.dc_strings = config_entry.data[CONF_DC_STRINGS]
    enasolar.max_output = config_entry.data[CONF_MAX_OUTPUT]

    _LOGGER.debug(
        "Max Output: %s, DC Strings: %s, Capability: %s",
        enasolar.max_output,
        enasolar.dc_strings,
        enasolar.capability,
    )

    enasolar.setup_sensors()
    for sensor in enasolar.sensors:
        _LOGGER.debug("Setup sensor %s", sensor.key)
        if sensor.enabled:
            if sensor.is_meter:
                hass_meter_sensors.append(
                    EnaSolarSensor(
                        sensor, config_entry.data[CONF_NAME], enasolar.serial_no
                    )
                )
            else:
                hass_data_sensors.append(
                    EnaSolarSensor(
                        sensor, config_entry.data[CONF_NAME], enasolar.serial_no
                    )
                )

    async_add_entities([*hass_meter_sensors, *hass_data_sensors])

    async def _async_enasolar_meters(hass,enasolar):
        """Update the EnaSolar Meter sensors."""

        if is_up(hass):
            values = await enasolar.read_meters()
        else:
            values = False

        for sensor in hass_meter_sensors:
            state_unknown = False
            if not values and (
                (sensor.sensor.per_day_basis and date.today() > sensor.sensor.date)
                or (
                    not sensor.sensor.per_day_basis
                    and not sensor.sensor.per_total_basis
                )
            ):
                state_unknown = True
            sensor.async_update_values(unknown_state=state_unknown)
            _LOGGER.debug(
                "Meter Sensor %s updated => %s", sensor.sensor.key, sensor.native_value
            )
        return values

    async def _async_enasolar_data(hass,enasolar):
        """Update the EnaSolar Data sensors."""

        if is_up(hass):
            values = await enasolar.read_data()
        else:
            values = False

        for sensor in hass_data_sensors:
            state_unknown = False
            if not values and (
                (sensor.sensor.per_day_basis and date.today() > sensor.sensor.date)
                or (
                    not sensor.sensor.per_day_basis
                    and not sensor.sensor.per_total_basis
                )
            ):
                state_unknown = True
            sensor.async_update_values(unknown_state=state_unknown)
            _LOGGER.debug(
                "Data Sensor %s updated => %s", sensor.sensor.key, sensor.native_value
            )
        return values

class EnaSolarSensor(CoordinatorEntity,SensorEntity):
    """Representation of a EnaSolar sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        pyenasolar_sensor,
        inverter_name: str = None,
        serial_no: str = None
    ) -> None:
        """Initialize the EnaSolar sensor."""
        super().__init__(coordinator)
        self.sensor = pyenasolar_sensor
        if inverter_name:
            self._attr_name = f"{inverter_name}_{self.sensor.name}"
        else:
            self._attr_name = f"enasolar_{self.sensor.name}"
        self.serial_no = serial_no
        self._native_value = self.sensor.value

        if pyenasolar_sensor.is_meter:
            self._attr_state_class = STATE_CLASS_MEASUREMENT
        else:
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
        self._attr_native_unit_of_measurement = ENASOLAR_UNIT_MAPPINGS[self.sensor.unit]

    @property
    def native_value(self):
        """Return the current sensor value."""
        return self._native_value

    @property
    def device_class(self):
        """Return the device class the sensor belongs to."""
        if self._attr_native_unit_of_measurement == POWER_KILO_WATT:
            return DEVICE_CLASS_POWER
        if self._attr_native_unit_of_measurement == ENERGY_KILO_WATT_HOUR:
            return DEVICE_CLASS_ENERGY
        if self._attr_native_unit_of_measurement in (TEMP_CELSIUS, TEMP_FAHRENHEIT):
            return DEVICE_CLASS_TEMPERATURE
        return None

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return f"{self.serial_no}_{self.sensor.name}"
