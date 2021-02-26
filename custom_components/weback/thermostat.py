"""Support for Weback Weback thermostats."""
import logging
import datetime

import weback_unofficial.thermosat as wb_thermostat

from homeassistant.components.climate import (
    ATTR_TEMPERATURE, STATE_HEAT, STATE_IDLE,
    SUPPORT_TARGET_TEMPERATURE, ClimateDevice)
from homeassistant.const import CONF_SCAN_INTERVAL

from . import WEBACK_DEVICES_THERMOSTAT, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

ATTR_ERROR = "error"
ATTR_COMPONENT_PREFIX = "component_"

SUPPORT_WEBACK = (
    SUPPORT_TARGET_TEMPERATURE
    | SUPPORT_OPERATION_MODE
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Weback thermostats."""
    thermostats = []
    for device in hass.data[WEBACK_DEVICES_THERMOSTAT]:
        thermostats.append(WebackThermostat(device, SCAN_INTERVAL))
    _LOGGER.debug("Adding Weback thermostats to Home Assistant: %s", thermostats)
    add_entities(thermostats, True)


class WebackThermostat(ClimateDevice):
    """Weback thermostats such as floureon BYC17GH3"""

    def __init__(self, device: wb_thermostat.Thermostat, scan_interval: datetime.timedelta):
        """Initialize the Weback Thermostat."""
        self.device = device
        self.scan_interval: datetime.timedelta = scan_interval
        self.last_fetch = None
        _LOGGER.debug("thermostat initialized: %s", self.name)

    def update(self):
        """Update device's state"""
        self.device.update()

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        if self.last_fetch is None:
            return True
        if (
            datetime.datetime.now() - self.last_fetch
        ).total_seconds() > self.scan_interval.total_seconds():
            return True
        return False

    @property
    def unique_id(self) -> str:
        """Return an unique ID."""
        return self.device.name

    @property
    def available(self):
        """Returns true if thermostat is online"""
        return self.device.is_available

    @property
    def supported_features(self):
        """Return the list of supported features."""
        supports = SUPPORT_TARGET_TEMPERATURE

        return supports    

    @property
    def is_heating(self):
        """Return true if thermostat is currently heating."""
        return STATE_HEAT if self.device.is_heating else STATE_IDLE

    @property
    def name(self):
        """Return the name of the device."""
        return self.device.nickname

    @property
    def temperature(self):
        """Return the current temperature of the device"""
        return self.device.temperature

    def set_temp(self,**kwargs):
        """Sets the target temperature of the device"""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        self.device.setTemp(temperature)