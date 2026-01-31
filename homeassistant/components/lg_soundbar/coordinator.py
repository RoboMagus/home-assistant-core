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

    powerstatus: bool = False
    auto_volume: bool = False
    night_mode: bool = False
    volume: int = 0
    volume_min: int = 0
    volume_max: int = 0
    function: int = -1
    functions: list = field(default_factory=list)
    equaliser: int = -1
    equalisers: list = field(default_factory=list)
    mute: bool = False
    rear_volume: int = 0
    rear_volume_min: int = 0
    rear_volume_max: int = 0
    woofer_volume: int = 0
    woofer_volume_min: int = 0
    woofer_volume_max: int = 0
    bass: int = 0
    treble: int = 0


type LGSoundbarConfigEntry = ConfigEntry[LGSoundbarCoordinator]


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
        self.device = None

        self.device_name = None
        self.settings_list = []
        self.data = LGSoundbarData()  # Default initialize

    async def _async_setup(self) -> None:
        """Set up device communication."""
        self.device = temescal.temescal(
            address=self.config_entry.data[CONF_HOST],
            port=self.config_entry.data[CONF_PORT],
            callback=self.handle_temescal_event,
        )
        self.device.get_product_info()
        self.device.get_mac_info()
        self.temescal_update()

    async def _async_update_data(self) -> LGSoundbarData:
        """Get LG Soundbar data."""
        self.temescal_update()
        return self.data

    def temescal_update(self) -> None:
        """Trigger updates from the device."""
        LOGGER.debug("temescal_update()")
        self.device.get_eq()
        self.device.get_info()
        self.device.get_func()
        self.device.get_settings()

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
            if "i_curr_eq" in data:
                current_state.equaliser = data["i_curr_eq"]
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
            if "b_powerstatus" in data:
                current_state.powerstatus = data["b_powerstatus"]
        elif response["msg"] == "FUNC_VIEW_INFO":
            if "i_curr_func" in data:
                current_state.function = data["i_curr_func"]
            if "ai_func_list" in data:
                current_state.functions = data["ai_func_list"]
        elif response["msg"] == "SETTING_VIEW_INFO":
            self.settings_list = data.keys()
            if "b_auto_vol" in data:
                current_state.auto_volume = data["b_auto_vol"]
            if "b_night_time" in data:
                current_state.night_mode = data["b_night_time"]
            if "i_rear_min" in data:
                current_state.rear_volume_min = data["i_rear_min"]
            if "i_rear_max" in data:
                current_state.rear_volume_max = data["i_rear_max"]
            if "i_rear_level" in data:
                current_state.rear_volume = data["i_rear_level"]
            if "i_woofer_min" in data:
                current_state.woofer_volume_min = data["i_woofer_min"]
            if "i_woofer_max" in data:
                current_state.woofer_volume_max = data["i_woofer_max"]
            if "i_woofer_level" in data:
                current_state.woofer_volume = data["i_woofer_level"]
            if "i_curr_eq" in data:
                current_state.equaliser = data["i_curr_eq"]
            if "s_user_name" in data:
                self.device_name = data["s_user_name"]

        LOGGER.debug("CurrentState: %r", current_state)
        self.hass.loop.call_soon_threadsafe(self.async_set_updated_data, current_state)

    def set_power(self, status: bool) -> None:
        """Set the media player state."""
        self.device.send_packet(
            {"cmd": "set", "data": {"b_powerkey": status}, "msg": "SPK_LIST_VIEW_INFO"}
        )

    def set_night_mode(self, enable: bool) -> None:
        """Enable / Disable night mode."""
        self.device.send_packet(
            {"cmd": "set", "data": {"b_night_time": enable}, "msg": "SETTING_VIEW_INFO"}
        )
