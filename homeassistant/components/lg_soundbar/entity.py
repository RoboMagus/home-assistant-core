"""Base Entity for LG Soundbar."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LGSoundbarCoordinator


class LGSoundbarEntity(CoordinatorEntity[LGSoundbarCoordinator]):
    """Defines a base LG Soundbar entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: LGSoundbarCoordinator) -> None:
        """Initialize the LG Soundbar entity."""
        super().__init__(coordinator)

        self._unique_id_base = (
            self.coordinator.config_entry.unique_id
            or self.coordinator.config_entry.entry_id
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._unique_id_base)},
            name=self.coordinator.config_entry.data[CONF_HOST],
        )
