"""Support for LG Soundbar number entities."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS, EntityCategory
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.enum import try_parse_enum

from .coordinator import LGSoundbarConfigEntry, LGSoundbarCoordinator, LGSoundbarData
from .entity import LGSoundbarEntity


@dataclass(frozen=True, kw_only=True)
class LGSoundbarNumberEntityDescription(NumberEntityDescription):
    """Describes LG Soundbar number entity."""

    set_fn: Callable[
        [LGSoundbarCoordinator, str], Callable[[], Coroutine[Any, Any, None]]
    ]


LGSOUNDBAR_NUMBERS: tuple[LGSoundbarNumberEntityDescription, ...] = (
    LGSoundbarNumberEntityDescription(
        key="bass",
        name="bass",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_max_value=5,
        native_min_value=-5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        set_fn=lambda coordinator, value: coordinator.set_bass_level(value),
    ),
    LGSoundbarNumberEntityDescription(
        key="treble",
        name="treble",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_max_value=5,
        native_min_value=-5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        set_fn=lambda coordinator, value: coordinator.set_treble_level(value),
    ),
    LGSoundbarNumberEntityDescription(
        key="center_volume",
        name="center volume",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        set_fn=lambda coordinator, value: coordinator.set_center_level(value),
    ),
    LGSoundbarNumberEntityDescription(
        key="rear_volume",
        name="rear volume",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        set_fn=lambda coordinator, value: coordinator.set_rear_level(value),
    ),
    LGSoundbarNumberEntityDescription(
        key="top_volume",
        name="top volume",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        set_fn=lambda coordinator, value: coordinator.set_top_level(value),
    ),
    LGSoundbarNumberEntityDescription(
        key="woofer_volume",
        name="woofer volume",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        set_fn=lambda coordinator, value: coordinator.set_woofer_level(value),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: LGSoundbarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Platform setup using common elements."""

    async_add_entities(
        LGSoundbarNumber(config_entry.runtime_data, description)
        for description in LGSOUNDBAR_NUMBERS
    )


class LGSoundbarNumber(LGSoundbarEntity, NumberEntity):
    """Defines an LGSoundbar number entity."""

    def __init__(
        self,
        coordinator: LGSoundbarCoordinator,
        description: LGSoundbarNumberEntityDescription,
    ) -> None:
        """Initialize LG Soundbar number."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._unique_id_base}_{description.key}_number"
        self._attr_name = f"{self.coordinator.device_name} {description.name}"

        self._attr_native_min_value = description.native_min_value or getattr(
            self.coordinator.data, self.entity_description.key + "_min"
        )
        self._attr_native_max_value = description.native_max_value or getattr(
            self.coordinator.data, self.entity_description.key + "_max"
        )

    @property
    def native_value(self) -> int | None:
        """Return the state of the number."""
        # LG Soundbar reports active value as steps away from min_value, so apply offset here!
        return self._attr_native_min_value + getattr(
            self.coordinator.data, self.entity_description.key
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the selected value."""
        # LG Soundbar reports active value as steps away from min_value, so apply offset here!
        self.entity_description.set_fn(
            self.coordinator, int(value - self._attr_native_min_value)
        )
