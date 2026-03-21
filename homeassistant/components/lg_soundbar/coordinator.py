"""Coordinator for the LG Soundbar integration."""

from dataclasses import dataclass, field
import logging

import temescal

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)


@dataclass
class LGSoundbarData:
    """LG Soundbar data."""

    # Settings
    powerstatus: bool = False
    auto_volume: bool = False
    night_mode: bool = False
    back_light: int = 0
    volume: int = 0
    volume_min: int = 0
    volume_max: int = 0
    function: int = -1
    functions: list = field(default_factory=list)
    equaliser: int = -1
    equalisers: list = field(default_factory=list)
    mute: bool = False
    center_volume: int = 0
    center_volume_min: int = 0
    center_volume_max: int = 0
    rear_volume: int = 0
    rear_volume_min: int = 0
    rear_volume_max: int = 0
    top_volume: int = 0
    top_volume_min: int = 0
    top_volume_max: int = 0
    woofer_volume: int = 0
    woofer_volume_min: int = 0
    woofer_volume_max: int = 0
    bass: int = 0
    treble: int = 0

    # Playback info
    support_play_ctrl: bool = False
    stream_type: int = 0
    play_ctrl: int = -1
    albumart: str|None = None
    artist: str|None = None
    title: str|None = None

    # processed values
    sound_mode: str|None = None
    sound_mode_list: list = field(default_factory=list)
    source: str|None = None
    source_list: list = field(default_factory=list)

type LGSoundbarConfigEntry = ConfigEntry[LGSoundbarCoordinator]

def get_sound_mode_from_equaliser(equaliser: int) -> str | None:
    if 0 <= equaliser < len(temescal.equalisers):
        return temescal.equalisers[equaliser]
    return None

def get_sound_mode_list_from_equalisers(equalisers) -> list[str]:
    return sorted(
        temescal.equalisers[equaliser]
        for equaliser in equalisers
        if equaliser < len(temescal.equalisers)
    )

def get_source_from_function(function: int) -> str | None:
    if 0 <= function < len(temescal.functions):
        return temescal.functions[function]
    return None

def get_source_list_from_functions(functions: list) -> list[str]:
    return sorted(
        temescal.functions[function]
        for function in functions
        if function < len(temescal.functions)
    )

class LGSoundbarCoordinator(DataUpdateCoordinator[LGSoundbarData]):
    """Coordinator to handle data updates LG Soundbar entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: LGSoundbarConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN}_{config_entry.unique_id}",
        )

        self._device = None
        self.device_name = None
        self.settings_list = []
        self.data = LGSoundbarData()  # Default initialize

    async def _async_setup(self) -> None:
        """Set up device communication."""
        self._device = temescal.temescal(
            address=self.config_entry.data[CONF_HOST],
            port=self.config_entry.data[CONF_PORT],
            callback=self.handle_temescal_event,
        )
        self._device.get_product_info()
        self._device.get_mac_info()
        self.temescal_update()

    async def _async_update_data(self) -> LGSoundbarData:
        """Get LG Soundbar data."""
        self.temescal_update()
        return self.data

    def temescal_update(self) -> None:
        """Trigger updates from the device."""
        LOGGER.debug("temescal_update()")
        self._device.get_eq()
        self._device.get_info()
        self._device.get_func()
        self._device.get_settings()
        self._device.get_play()

    def handle_temescal_event(self, response) -> None:
        """Handle responses from the speakers."""
        LOGGER.debug("Temescal event: %s", response)
        current_state = self.data
        data = response.get("data") or {}
        if response["msg"] == "EQ_VIEW_INFO":
            if "i_bass" in data:
                current_state.bass = data["i_bass"]
            if "i_treble" in data:
                current_state.treble = data["i_treble"]
            if "ai_eq_list" in data:
                current_state.equalisers = data["ai_eq_list"]
                current_state.sound_mode_list = get_sound_mode_list_from_equalisers(current_state.equalisers)
            if "i_curr_eq" in data:
                current_state.equaliser = data["i_curr_eq"]
                current_state.sound_mode = get_sound_mode_from_equaliser(current_state.equaliser)
        elif response["msg"] == "SPK_LIST_VIEW_INFO":
            if "i_vol" in data:
                current_state.volume = data["i_vol"]
            if "i_vol_min" in data:
                current_state.volume_min = data["i_vol_min"]
            if "i_vol_max" in data:
                current_state.volume_max = data["i_vol_max"]
            if "b_mute" in data:
                current_state.mute = data["b_mute"]
            if "i_curr_func" in data:
                current_state.function = data["i_curr_func"]
                current_state.source = get_source_from_function(current_state.function)
            if "b_powerstatus" in data:
                current_state.powerstatus = data["b_powerstatus"]
        elif response["msg"] == "FUNC_VIEW_INFO":
            if "i_curr_func" in data:
                current_state.function = data["i_curr_func"]
                current_state.source = get_source_from_function(current_state.function)
            if "ai_func_list" in data:
                current_state.functions = data["ai_func_list"]
                current_state.source_list = get_source_list_from_functions(current_state.functions)
        elif response["msg"] == "SETTING_VIEW_INFO":
            self.settings_list = data.keys()
            if "b_auto_vol" in data:
                current_state.auto_volume = data["b_auto_vol"]
            if "b_night_time" in data:
                current_state.night_mode = data["b_night_time"]
            if "i_center_min" in data:
                current_state.center_volume_min = data["i_center_min"]
            if "i_center_max" in data:
                current_state.center_volume_max = data["i_center_max"]
            if "i_center_level" in data:
                current_state.center_volume = data["i_center_level"]
            if "i_rear_min" in data:
                current_state.rear_volume_min = data["i_rear_min"]
            if "i_rear_max" in data:
                current_state.rear_volume_max = data["i_rear_max"]
            if "i_rear_level" in data:
                current_state.rear_volume = data["i_rear_level"]
            if "i_top_min" in data:
                current_state.top_volume_min = data["i_top_min"]
            if "i_top_max" in data:
                current_state.top_volume_max = data["i_top_max"]
            if "i_top_level" in data:
                current_state.top_volume = data["i_top_level"]
            if "i_woofer_min" in data:
                current_state.woofer_volume_min = data["i_woofer_min"]
            if "i_woofer_max" in data:
                current_state.woofer_volume_max = data["i_woofer_max"]
            if "i_woofer_level" in data:
                current_state.woofer_volume = data["i_woofer_level"]
            if "i_curr_eq" in data:
                current_state.equaliser = data["i_curr_eq"]
                current_state.sound_mode = get_sound_mode_from_equaliser(current_state.equaliser)
            if "i_back_light" in data:
                current_state.back_light = data["i_back_light"]
            if "s_user_name" in data:
                self.device_name = data["s_user_name"]
        elif response["msg"] == "PLAY_INFO":
            if not data :
                current_state.play_ctrl = -1
                current_state.albumart = None
                current_state.artist = None
                current_state.title = None
            if "b_support_play_ctrl" in data:
                current_state.support_play_ctrl = data["b_support_play_ctrl"]
            if "i_stream_type" in data:
                current_state.stream_type = data["i_stream_type"]
                if self.data.stream_type != current_state.stream_type:
                    self._device.get_play()
                if current_state.stream_type == 0:
                    current_state.albumart = None
                    current_state.artist = None
                    current_state.title = None
            if "i_play_ctrl" in data:
                current_state.play_ctrl = data["i_play_ctrl"]
            if "s_albumart" in data:
                current_state.albumart = data["s_albumart"].strip() or None
            if "s_artist" in data:
                current_state.artist = data["s_artist"].strip() or None
            if "s_title" in data:
                current_state.title = data["s_title"].strip() or None

        LOGGER.debug("CurrentState: %r", current_state)
        self.hass.loop.call_soon_threadsafe(self.async_set_updated_data, current_state)

    def set_power(self, status: bool) -> None:
        """Set the media player state."""
        self._device.send_packet(
            {"cmd": "set", "data": {"b_powerkey": status}, "msg": "SPK_LIST_VIEW_INFO"}
        )

    def set_source(self, source: str) -> None:
        """Set input source."""
        self._device.set_func(temescal.functions.index(source))

    def set_sound_mode(self, sound_mode: str) -> None:
        """Set sound mode."""
        self._device.set_eq(temescal.equalisers.index(sound_mode))

    def set_night_mode(self, enable: bool) -> None:
        """Enable / Disable night mode."""
        self._device.send_packet(
            {"cmd": "set", "data": {"b_night_time": enable}, "msg": "SETTING_VIEW_INFO"}
        )

    def set_mute(self, mute: bool) -> None:
        """Mute / Unmute."""
        self._device.set_mute(mute)

    def set_back_light(self, value: int) -> None:
        """Set backlight mode."""
        self._device.send_packet(
            {"cmd": "set", "data": {"i_back_light": value}, "msg": "SETTING_VIEW_INFO"}
        )

    def set_auto_volume(self, enable: bool) -> None:
        """Enable / Disable auto volume."""
        self._device.set_avc(enable)

    def set_volume(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume = volume * self.data.volume_max
        self._device.set_volume(int(volume))

    def set_bass_level(self, value: int) -> None:
        """Set bass level."""
        self._device.send_packet(
            {"cmd": "set", "data": {"i_bass": value}, "msg": "EQ_VIEW_INFO"}
        )

    def set_treble_level(self, value: int) -> None:
        """Set treble level."""
        self._device.send_packet(
            {"cmd": "set", "data": {"i_treble": value}, "msg": "EQ_VIEW_INFO"}
        )

    def set_center_level(self, value: int) -> None:
        """Set center level."""
        self._device.set_center_level(value)

    def set_rear_level(self, value: int) -> None:
        """Set rear level."""
        self._device.set_rear_level(value)

    def set_top_level(self, value: int) -> None:
        """Set top level."""
        self._device.set_top_level(value)

    def set_woofer_level(self, value: int) -> None:
        """Set woofer level."""
        self._device.set_woofer_level(value)

    def play_ctrl(self, value: bool):
        """Play / Pause control."""
        if self.data.support_play_ctrl:
            self._device.send_packet(
                {"cmd": "set", "data": {"i_play_ctrl": int(value)}, "msg": "PLAY_INFO"}
            )
