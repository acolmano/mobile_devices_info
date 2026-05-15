import re
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import config_validation as cv
from . import DOMAIN


def _phone_key(device) -> str:
    """Restituisce la chiave del campo telefono per un device."""
    name = device.name or device.id
    return "phone_" + re.sub(r"[^a-zA-Z0-9]", "_", name)


class MobileDevicesInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        # Singleton: impedisce la creazione di più istanze
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        device_registry = dr.async_get(self.hass)
        mobile_devices = [
            d for d in device_registry.devices.values()
            if any(ident[0] == "mobile_app" for ident in d.identifiers)
        ]

        if not mobile_devices:
            return self.async_abort(reason="no_devices")

        device_options = {
            d.id: d.name or d.name_by_user or "Dispositivo sconosciuto"
            for d in mobile_devices
        }

        if user_input is not None:
            return self.async_create_entry(
                title="Mobile Devices Info",
                data={},
            )

        schema = vol.Schema({
            vol.Required("notificare", default=[]): cv.multi_select(device_options)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MobileDevicesInfoOptionsFlowHandler(config_entry)


class MobileDevicesInfoOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        device_registry = dr.async_get(self.hass)
        mobile_devices = sorted(
            [
                d for d in device_registry.devices.values()
                if any(ident[0] == "mobile_app" for ident in d.identifiers)
            ],
            key=lambda d: d.name or "",
        )

        device_options = {
            d.id: d.name or d.name_by_user or "Dispositivo sconosciuto"
            for d in mobile_devices
        }

        current_notify = self.config_entry.options.get("notificare", [])
        current_phones = self.config_entry.options.get("phone_numbers", {})

        if user_input is not None:
            notificare = user_input.get("notificare", [])
            phone_numbers = {}
            for device in mobile_devices:
                key = _phone_key(device)
                phone = (user_input.get(key) or "").strip()
                if phone:
                    phone_numbers[device.id] = phone
            return self.async_create_entry(
                data={
                    "notificare": notificare,
                    "phone_numbers": phone_numbers,
                }
            )

        schema_dict = {
            vol.Optional("notificare", default=current_notify): cv.multi_select(device_options),
        }
        for device in mobile_devices:
            key = _phone_key(device)
            current_phone = current_phones.get(device.id, "")
            schema_dict[vol.Optional(key, default=current_phone)] = str

        schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
