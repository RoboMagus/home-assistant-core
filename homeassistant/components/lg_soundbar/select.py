"""Support for LG Soundbar select entities."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LGSoundbarConfigEntry, LGSoundbarCoordinator, LGSoundbarData
from .entity import LGSoundbarEntity


@dataclass(frozen=True, kw_only=True)
class LGSoundbarSelectEntityDescription(SelectEntityDescription):
    """Describes LG Soundbar select entity."""

    set_fn: Callable[
        [LGSoundbarCoordinator, str], Callable[[], Coroutine[Any, Any, None]]
    ]


LGSOUNDBAR_SELECTS: tuple[LGSoundbarSelectEntityDescription, ...] = (
    LGSoundbarSelectEntityDescription(
        key="back_light",
        name="backlight",
        options=["Auto Brightness", "Auto Off", "Always On"],
        entity_category=EntityCategory.CONFIG,
        set_fn=lambda coordinator, value_idx: coordinator.set_back_light(value_idx),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LGSoundbarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Platform setup using common elements."""

    async_add_entities(
        LGSoundbarSelect(config_entry.runtime_data, description)
        for description in LGSOUNDBAR_SELECTS
    )


class LGSoundbarSelect(LGSoundbarEntity, SelectEntity):
    """Defines an LGSoundbar select entity."""

    entity_description: LGSoundbarSelectEntityDescription

    def __init__(
        self,
        coordinator: LGSoundbarCoordinator,
        description: LGSoundbarSelectEntityDescription,
    ) -> None:
        """Initialize LGSoundbar select."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._unique_id_base}_{description.key}_select"
        self._attr_name = f"{self.coordinator.device_name} {description.name}"

    @property
    def current_option(self) -> str | None:
        """Return the state of the select."""
        value_idx = getattr(self.coordinator.data, self.entity_description.key)
        return self.entity_description.options[value_idx]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value_idx = self.entity_description.options.index(option)
        self.entity_description.set_fn(self.coordinator, value_idx)
