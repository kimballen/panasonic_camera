from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import logging
from datetime import timedelta
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    camera = hass.data[DOMAIN][config_entry.entry_id]
    scan_interval = config_entry.options.get("scan_interval", 10)

    async def async_update_data():
        """Fetch data from camera."""
        return await camera.get_io_status()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="panasonic_camera_sensors",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []
    for terminal in [1, 2, 3]:
        if terminal == 1 or camera.terminal_configs[terminal]['mode'].endswith('input'):
            entities.append(PanasonicCameraIOSensor(
                coordinator,
                camera,
                config_entry,
                terminal
            ))

    async_add_entities(entities)

class PanasonicCameraIOSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Panasonic Camera I/O sensor."""

    def __init__(self, coordinator, camera, config_entry, terminal):
        super().__init__(coordinator)
        self.camera = camera
        self.terminal = terminal
        self._attr_unique_id = f"{config_entry.entry_id}_terminal_{terminal}"
        self._attr_name = f"Camera {camera.ip} Terminal {terminal}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"Panasonic Camera {camera.ip}",
            "manufacturer": "Panasonic",
            "model": "WV-NW502",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data and isinstance(self.coordinator.data, dict):
            if self.terminal in self.coordinator.data:
                return self.coordinator.data[self.terminal]['state']
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        if self.coordinator.data and isinstance(self.coordinator.data, dict):
            if self.terminal in self.coordinator.data:
                return {
                    "raw_state": self.coordinator.data[self.terminal]['raw_state'],
                    "mode": self.camera.terminal_configs[self.terminal]['mode']
                }
        return {}

