"""Support for LG Soundbar switch entities."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LGSoundbarConfigEntry, LGSoundbarCoordinator
from .entity import LGSoundbarEntity


@dataclass(frozen=True, kw_only=True)
class LGSoundbarSwitchEntityDescription(SwitchEntityDescription):
    """Describes LG Soundbar switch entity."""

    set_fn: Callable[
        [LGSoundbarCoordinator, bool], Callable[[], Coroutine[Any, Any, None]]
    ]


LGSOUNDBAR_SWITCHES: tuple[LGSoundbarSwitchEntityDescription, ...] = (
    LGSoundbarSwitchEntityDescription(
        key="auto_volume",
        name="auto volume",
        entity_category=EntityCategory.CONFIG,
        set_fn=lambda coordinator, on: coordinator.device.set_avc(on),
    ),
    LGSoundbarSwitchEntityDescription(
        key="night_mode",
        name="night mode",
        entity_category=EntityCategory.CONFIG,
        set_fn=lambda coordinator, on: coordinator.set_night_mode(on),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LGSoundbarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Platform setup using common elements."""

    async_add_entities(
        LGSoundbarSwitch(config_entry.runtime_data, description)
        for description in LGSOUNDBAR_SWITCHES
    )


class LGSoundbarSwitch(LGSoundbarEntity, SwitchEntity):
    """LG Soundbar switch."""

    def __init__(
        self,
        coordinator: LGSoundbarCoordinator,
        description: LGSoundbarSwitchEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._unique_id_base}_{description.key}_switch"
        self._attr_name = f"{self.coordinator.device_name} {description.name}"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is turned on."""
        return getattr(self.coordinator.data, self.entity_description.key)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self.entity_description.set_fn(self.coordinator, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self.entity_description.set_fn(self.coordinator, True)
