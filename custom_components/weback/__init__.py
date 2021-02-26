"""Support for WeBack devices."""
from datetime import timedelta
import logging
import random
import string

import voluptuous as vol
from weback_unofficial.client import WebackApi
from weback_unofficial.vacuum import CleanRobot

from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "weback"
SCAN_INTERVAL = timedelta(seconds=60)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

WEBACK_DEVICES_VACUUM = "weback_devices_vacuum"
WEBACK_DEVICES_THERMOSTAT = "weback_devices_thermostat"

SUPPORTED_DEVICES = ["_CLEAN_ROBOT", "__THERMOSTAT"]


def setup(hass, config):
    """Set up the Weback component."""
    _LOGGER.debug("Creating new Weback component")

    hass.data[WEBACK_DEVICES_VACUUM] = []
    hass.data[WEBACK_DEVICES_THERMOSTAT] = []

    weback_api = WebackApi(
        config[DOMAIN].get(CONF_USERNAME), config[DOMAIN].get(CONF_PASSWORD),
    )

    devices = weback_api.device_list()
    _LOGGER.debug("Weback devices: %s", devices)

    for device in devices:
        _LOGGER.info(
            "Discovered Weback device %s with nickname %s",
            device["Thing_Name"],
            device["Thing_Nick_Name"],
        )

        # Fetching device description to check if this device is supported by platform
        description = weback_api.get_device_description(device["Thing_Name"])
        if description.get("thingTypeName") not in SUPPORTED_DEVICES:
            _LOGGER.info("Device not supported by this integration")
            continue

        if description.get("thingTypeName") == '_CLEAN_ROBOT':
            vacuum = CleanRobot(device["Thing_Name"], weback_api, None, description)
            hass.data[WEBACK_DEVICES_VACUUM].append(vacuum)
        else:
            thermostat = Thermostat(device["Thing_Name"], weback_api, None, description)
            hass.data[WEBACK_DEVICES_THERMOSTAT].append(thermostat)


    if hass.data[WEBACK_DEVICES_VACUUM]:
        _LOGGER.debug("Starting vacuum and thermostat components")
        discovery.load_platform(hass, "vacuum", DOMAIN, {}, config)

    if hass.data[WEBACK_DEVICES_THERMOSTAT]:
        _LOGGER.debug("Starting vacuum and thermostat components")
        discovery.load_platform(hass, "vacuum", DOMAIN, {}, config)

    return True
