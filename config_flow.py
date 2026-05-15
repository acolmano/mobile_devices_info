import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import config_validation as cv
from . import DOMAIN

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
            # Creazione entry: salva dati vuoti, le opzioni saranno nell'options flow
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
        mobile_devices = [
            d for d in device_registry.devices.values()
            if any(ident[0] == "mobile_app" for ident in d.identifiers)
        ]

        device_options = {
            d.id: d.name or d.name_by_user or "Dispositivo sconosciuto"
            for d in mobile_devices
        }

        current = self.config_entry.options.get("notificare", [])

        if user_input is not None:
            # Salva le opzioni correttamente senza title o options
            return self.async_create_entry(
                data={"notificare": user_input.get("notificare", [])}
            )

        schema = vol.Schema({
            vol.Optional("notificare", default=current): cv.multi_select(device_options)
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors={},
        )
