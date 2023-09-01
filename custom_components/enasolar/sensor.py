"""EnaSolar solar inverter interface."""

from __future__ import annotations
from datetime import date, timedelta
import logging

from homeassistant.components.sensor import (
    SensorStateClass,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.sun import is_up

from .const import (
    CONF_CAPABILITY,
    CONF_DC_STRINGS,
    CONF_MAX_OUTPUT,
    DOMAIN,
    ENASOLAR_UNIT_MAPPINGS,
    SCAN_METERS_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Add enasolar entry."""

    enasolar = hass.data[DOMAIN][entry.entry_id]
    enasolar.capability = entry.data[CONF_CAPABILITY]
    enasolar.dc_strings = entry.data[CONF_DC_STRINGS]
    enasolar.max_output = entry.data[CONF_MAX_OUTPUT]
    enasolar.inverter_name = entry.data[CONF_NAME]

    coordinator = EnaSolarCoordinator(hass, enasolar)

    # Use all sensors by default, but split them to have two update frequencies
    enasolar.meter_sensors = []
    enasolar.data_sensors = []

    _LOGGER.debug(
        "Max Output: %s, DC Strings: %s, Capability: %s",
        enasolar.max_output,
        enasolar.dc_strings,
        enasolar.capability,
    )

    enasolar.setup_sensors()
    for sensor in enasolar.sensors:
        _LOGGER.debug("Setup sensor entity: %s", sensor.key)
        if sensor.enabled:
            if sensor.is_meter:
                enasolar.meter_sensors.append(
                    EnaSolarEntity(
                        coordinator, sensor, enasolar.inverter_name, enasolar.serial_no
                    )
                )
            else:
                enasolar.data_sensors.append(
                    EnaSolarEntity(
                        coordinator, sensor, enasolar.inverter_name, enasolar.serial_no
                    )
                )

    async_add_entities([*enasolar.meter_sensors, *enasolar.data_sensors])

    await coordinator.async_config_entry_first_refresh()


class EnaSolarEntity(CoordinatorEntity, SensorEntity):
    """Representation of a EnaSolar sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        pyenasolar_sensor,
        inverter_name: str = None,
        serial_no: str = None
    ) -> None:
        """Initialize the EnaSolar sensor."""

        self.sensor = pyenasolar_sensor
        super().__init__(coordinator)

        if inverter_name:
            self._attr_name = f"{inverter_name}_{self.sensor.name}"
        else:
            self._attr_name = f"enasolar_{self.sensor.name}"
        self.serial_no = serial_no
        self._native_value = self.sensor.value

        if pyenasolar_sensor.is_meter:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = ENASOLAR_UNIT_MAPPINGS[self.sensor.unit]

    @property
    def native_value(self):
        """Return the current sensor value."""
        return self._native_value

    @property
    def device_class(self):
        """Return the device class the sensor belongs to."""
        if self._attr_native_unit_of_measurement == UnitOfPower.WATT:
            return SensorDeviceClass.POWER
        if self._attr_native_unit_of_measurement == UnitOfEnergy.WATT_HOUR:
            return SensorDeviceClass.ENERGY
        if self._attr_native_unit_of_measurement in (
            UnitOfTemperature.CELSIUS,
            UnitOfTemperature.FAHRENHEIT,
        ):
            return SensorDeviceClass.TEMPERATURE
        if self._attr_native_unit_of_measurement in (
            UnitOfTime.HOURS,
            UnitOfTime.DAYS,
        ):
            return SensorDeviceClass.DURATION
        return None

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return f"{self.serial_no}_{self.sensor.name}"

    @callback
    def async_update_values(self, unknown_state=False):
        """Update this sensor."""
        update = False

        if self.sensor.value != self._native_value:
            update = True
            self._native_value = self.sensor.value

        if unknown_state and self._native_value is not None:
            update = True
            self._native_value = None

        if update:
            self.async_write_ha_state()

class EnaSolarCoordinator(DataUpdateCoordinator):
    """Cordinator for EnaSolar Inverter Sensors."""

    def __init__(self, hass: HomeAssistant, enasolar) -> None:
        super().__init__(
            hass,
             _LOGGER,
            name="EnaSolar Inverter",
            update_interval=timedelta(seconds=SCAN_METERS_INTERVAL),
        )
        self.hass = hass
        self.enasolar = enasolar

    async def _async_update_data(self):
        """Get the sensor data from the inverter."""

        if is_up(self.hass):
            meter_values = await self.enasolar.read_meters()
        else:
            meter_values = False

        for sensor in self.enasolar.meter_sensors:
            state_unknown = False
            if not meter_values and (
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

        if is_up(self.hass):
            data_values = await self.enasolar.read_data()
        else:
            data_values = False

        for sensor in self.enasolar.data_sensors:
            state_unknown = False
            if not data_values and (
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

        return meter_values + data_values
