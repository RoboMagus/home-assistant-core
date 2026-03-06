"""Support for LG soundbars."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import LGSoundbarEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up media_player from a config entry created in the integrations UI."""
    async_add_entities([LGDevice(config_entry.runtime_data)])


class LGDevice(LGSoundbarEntity, MediaPlayerEntity):
    """Representation of an LG soundbar device."""

    _attr_should_poll = False
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
    )
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator) -> None:
        """Initialize the LG speakers."""
        super().__init__(coordinator)
        self._attr_unique_id = self._unique_id_base
        self._attr_name = self.coordinator.device_name

    @property
    def state(self) -> MediaPlayerState:
        """State of the player."""
        if self.coordinator.data.powerstatus:
            if self.coordinator.data.support_play_ctrl:
                if self.coordinator.data.play_ctrl == 0:
                    return MediaPlayerState.PLAYING
                return MediaPlayerState.PAUSED
            return MediaPlayerState.ON

        return MediaPlayerState.OFF

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media, music track only."""
        return self.coordinator.data.artist

    @property
    def media_image_url(self) -> str | None:
        """Image url of current playing media."""
        return self.coordinator.data.albumart

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        return self.coordinator.data.title

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        if self.coordinator.data.volume_max != 0:
            return self.coordinator.data.volume / self.coordinator.data.volume_max
        return 0

    @property
    def is_volume_muted(self) -> bool | None:
        """Boolean if volume is currently muted."""
        return self.coordinator.data.mute

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode."""
        return self.coordinator.data.sound_mode

    @property
    def sound_mode_list(self) -> list[str] | None:
        """Return the available sound modes."""
        return self.coordinator.data.sound_mode_list

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        return self.coordinator.data.source

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        return self.coordinator.data.source_list

    def set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        self.coordinator.set_volume(volume)

    def mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        self.coordinator.set_mute(mute)

    def select_source(self, source: str) -> None:
        """Select input source."""
        self.coordinator.set_source(source)

    def select_sound_mode(self, sound_mode: str) -> None:
        """Set Sound Mode for Receiver.."""
        self.coordinator.set_sound_mode(sound_mode)

    def turn_on(self) -> None:
        """Turn the media player on."""
        self.coordinator.set_power(True)

    def turn_off(self) -> None:
        """Turn the media player off."""
        self.coordinator.set_power(False)

    def media_play(self) -> None:
        """Send play command."""
        self.coordinator.play_ctrl(False)

    def media_pause(self) -> None:
        """Send pause command."""
        self.coordinator.play_ctrl(True)
