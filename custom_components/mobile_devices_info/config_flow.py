import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from . import DOMAIN


def _validate_phone_sms(phone: str, sms_enabled: bool) -> dict:
    """Valida il numero di telefono e l'abilitazione SMS. Restituisce un dizionario di errori."""
    errors = {}
    if phone and len(phone) < 10:
        errors["phone_number"] = "phone_number_too_short"
    if sms_enabled and len(phone) < 10:
        errors["notifica_sms"] = "sms_requires_valid_phone"
    return errors


class MobileDevicesInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(title="Mobile Devices Info", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {
            "device": RegisteredDeviceSubentryFlow,
            "manual_device": ManualDeviceSubentryFlow,
        }


class RegisteredDeviceSubentryFlow(ConfigSubentryFlow):
    """Flusso per dispositivi registrati in HA (mobile_app)."""

    async def async_step_user(self, user_input=None) -> SubentryFlowResult:
        device_registry = dr.async_get(self.hass)
        mobile_devices = [
            d for d in device_registry.devices.values()
            if any(ident[0] == "mobile_app" for ident in d.identifiers)
        ]

        config_entry = self._get_entry()
        configured_ids = {
            sub.data["device_id"]
            for sub in config_entry.subentries.values()
            if sub.data.get("device_id")
        }
        available = [d for d in mobile_devices if d.id not in configured_ids]

        if not available:
            return self.async_abort(reason="no_devices_available")

        device_options = [
            {"value": d.id, "label": d.name or d.name_by_user or "Dispositivo sconosciuto"}
            for d in sorted(available, key=lambda d: d.name or "")
        ]

        errors = {}

        if user_input is not None:
            phone = (user_input.get("phone_number") or "").strip()
            sms_enabled = user_input.get("notifica_sms", False)
            errors = _validate_phone_sms(phone, sms_enabled)

            if not errors:
                device_id = user_input["device_id"]
                device = device_registry.devices.get(device_id)
                return self.async_create_entry(
                    title=device.name if device else device_id,
                    data={
                        "device_id": device_id,
                        "phone_number": phone or None,
                        "notificare": user_input.get("notificare", False),
                        "notifica_sms": sms_enabled,
                    },
                )

        schema = vol.Schema({
            vol.Required("device_id"): SelectSelector(
                SelectSelectorConfig(
                    options=device_options,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional("phone_number"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notificare"): BooleanSelector(),
            vol.Optional("notifica_sms"): BooleanSelector(),
        })

        suggested = user_input if user_input else {
            "phone_number": "",
            "notificare": False,
            "notifica_sms": False,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None) -> SubentryFlowResult:
        config_entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        errors = {}

        if user_input is not None:
            phone = (user_input.get("phone_number") or "").strip()
            sms_enabled = user_input.get("notifica_sms", False)
            errors = _validate_phone_sms(phone, sms_enabled)

            if not errors:
                return self.async_update_and_abort(
                    entry=config_entry,
                    subentry=subentry,
                    title=subentry.title,
                    data_updates={
                        "phone_number": phone or None,
                        "notificare": user_input.get("notificare", False),
                        "notifica_sms": sms_enabled,
                    },
                )

        schema = vol.Schema({
            vol.Optional("phone_number"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notificare"): BooleanSelector(),
            vol.Optional("notifica_sms"): BooleanSelector(),
        })

        suggested = user_input if user_input else {
            "phone_number": subentry.data.get("phone_number") or "",
            "notificare": subentry.data.get("notificare", False),
            "notifica_sms": subentry.data.get("notifica_sms", False),
        }

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
            errors=errors,
        )


class ManualDeviceSubentryFlow(ConfigSubentryFlow):
    """Flusso per dispositivi manuali (non registrati in HA)."""

    async def async_step_user(self, user_input=None) -> SubentryFlowResult:
        errors = {}

        if user_input is not None:
            phone = (user_input.get("phone_number") or "").strip()
            sms_enabled = user_input.get("notifica_sms", False)
            errors = _validate_phone_sms(phone, sms_enabled)

            if not errors:
                name = (user_input.get("custom_name") or "").strip()
                return self.async_create_entry(
                    title=name or "Device manuale",
                    data={
                        "device_id": None,
                        "custom_name": name,
                        "note": (user_input.get("note") or "").strip() or None,
                        "phone_number": phone or None,
                        "notifica_sms": sms_enabled,
                    },
                )

        schema = vol.Schema({
            vol.Required("custom_name"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Optional("note"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Optional("phone_number"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notifica_sms"): BooleanSelector(),
        })

        suggested = user_input if user_input else {
            "custom_name": "",
            "note": "",
            "phone_number": "",
            "notifica_sms": False,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None) -> SubentryFlowResult:
        config_entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        errors = {}

        if user_input is not None:
            phone = (user_input.get("phone_number") or "").strip()
            sms_enabled = user_input.get("notifica_sms", False)
            errors = _validate_phone_sms(phone, sms_enabled)

            if not errors:
                name = (user_input.get("custom_name") or "").strip()
                return self.async_update_and_abort(
                    entry=config_entry,
                    subentry=subentry,
                    title=name or subentry.title,
                    data_updates={
                        "custom_name": name,
                        "note": (user_input.get("note") or "").strip() or None,
                        "phone_number": phone or None,
                        "notifica_sms": sms_enabled,
                    },
                )

        schema = vol.Schema({
            vol.Required("custom_name"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Optional("note"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Optional("phone_number"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notifica_sms"): BooleanSelector(),
        })

        suggested = user_input if user_input else {
            "custom_name": subentry.data.get("custom_name") or subentry.title,
            "note": subentry.data.get("note") or "",
            "phone_number": subentry.data.get("phone_number") or "",
            "notifica_sms": subentry.data.get("notifica_sms", False),
        }

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
            errors=errors,
        )
