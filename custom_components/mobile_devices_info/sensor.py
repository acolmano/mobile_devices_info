import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    sensor = MobileDevicesSensor(hass, entry)
    async_add_entities([sensor], True)


class MobileDevicesSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self.config_entry = config_entry
        self._attr_name = "Mobile Devices Info"
        self._attr_icon = "mdi:cellphone-information"

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.config_entry.add_update_listener(self._async_entry_updated)
        )

    async def _async_entry_updated(self, hass, entry):
        self.async_write_ha_state()

    def _get_devices(self):
        dev_reg = async_get_device_registry(self.hass)
        devices = []
        for subentry in self.config_entry.subentries.values():
            device_id = subentry.data.get("device_id")

            if device_id:
                # Device registrato in HA
                device = dev_reg.devices.get(device_id)
                if device is None:
                    _LOGGER.debug("Device %s non trovato nel registry", device_id)
                    continue
                identity = next(
                    (ident[1] for ident in device.identifiers if ident[0] == "mobile_app"),
                    None,
                )
                notify_name = (
                    "notify.mobile_app_" + subentry.title.lower().replace(" ", "_").replace("-", "_")
                    if subentry.title else None
                )
                devices.append({
                    "name": subentry.title,
                    "type": "registered",
                    "identity": identity,
                    "notify_id": f"notify.mobile_app_{identity}" if identity else None,
                    "notify_name": notify_name,
                    "notificare": subentry.data.get("notificare", False),
                    "notifica_sms": False,
                    "phone_number": subentry.data.get("phone_number"),
                    "note": None,
                })
            else:
                # Device non registrato (manuale)
                devices.append({
                    "name": subentry.data.get("custom_name") or subentry.title,
                    "type": "manual",
                    "identity": None,
                    "notify_id": None,
                    "notify_name": None,
                    "notificare": False,
                    "notifica_sms": subentry.data.get("notifica_sms", False),
                    "phone_number": subentry.data.get("phone_number"),
                    "note": subentry.data.get("note"),
                })
        return devices

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return len([d for d in self._get_devices() if d.get("notificare")])

    @property
    def extra_state_attributes(self):
        return {"devices": self._get_devices()}
