import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    sensor = MobileDevicesSensor(hass, entry)
    await sensor._load_phone_numbers()
    await sensor.async_update_options()
    async_add_entities([sensor], True)

class MobileDevicesSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self.config_entry = config_entry
        self._attr_name = "Mobile Devices Info"
        self._attr_icon = "mdi:cellphone-information"
        self._devices = []
        self.dev_reg = None
        self.phone_map = {}

    async def async_added_to_hass(self):
        self.dev_reg = async_get_device_registry(self.hass)
        self.async_on_remove(
            self.config_entry.add_update_listener(self._async_options_updated)
        )

    async def _load_phone_numbers(self):
        self.phone_map = {}
        fritz_entry = next(
            (e for e in self.hass.config_entries.async_entries("fritz_automation") if e.data),
            None,
        )
        if not fritz_entry:
            _LOGGER.debug("Nessuna integrazione fritz_automation trovata")
            return

        subentries = fritz_entry.as_dict().get("subentries", {})
        if isinstance(subentries, dict):
            items = subentries.values()
        else:
            items = subentries

        for sub in items:
            data = sub.get("data", {})
            name = data.get("name")
            target = data.get("target")
            if name and target:
                self.phone_map[name] = target

        _LOGGER.debug(f"Phone map aggiornata: {self.phone_map}")

    async def _async_options_updated(self, hass, entry):
        await self._load_phone_numbers()
        await self.async_update_options()
        self.async_write_ha_state()

    async def async_update_options(self):
        if self.dev_reg is None:
            self.dev_reg = async_get_device_registry(self.hass)

        notify_ids = set(self.config_entry.options.get("notificare", []))

        devices = []
        for device in self.dev_reg.devices.values():
            if any(ident[0] == "mobile_app" for ident in device.identifiers):
                identity = None
                for ident in device.identifiers:
                    if ident[0] == "mobile_app":
                        identity = ident[1]
                        break

                phone = self.phone_map.get(device.name, None)

                devices.append({
                    "name": device.name or "Unknown",
                    "identity": identity,
                    "notify_id": f"notify.mobile_app_{identity}",
                    "notificare": device.id in notify_ids,
                    "phone_number": phone,
                })

        self._devices = devices

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return len([d for d in self._devices if d.get("notificare")])

    @property
    def extra_state_attributes(self):
        return {"devices": self._devices}
