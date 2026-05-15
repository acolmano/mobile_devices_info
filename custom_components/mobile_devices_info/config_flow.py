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
        return {"device": DeviceSubentryFlowHandler}


class DeviceSubentryFlowHandler(ConfigSubentryFlow):

    async def async_step_user(self, user_input=None) -> SubentryFlowResult:
        """Step 1: menu con bottoni — dispositivo registrato o manuale."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["registered", "manual"],
        )

    async def async_step_registered(self, user_input=None) -> SubentryFlowResult:
        """Step 2a: seleziona dispositivo mobile_app registrato in HA."""
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

        if user_input is not None:
            device_id = user_input["device_id"]
            device = device_registry.devices.get(device_id)
            return self.async_create_entry(
                title=device.name if device else device_id,
                data={
                    "device_id": device_id,
                    "phone_number": (user_input.get("phone_number") or "").strip() or None,
                    "notificare": user_input.get("notificare", False),
                },
            )

        schema = vol.Schema({
            vol.Required("device_id"): SelectSelector(
                SelectSelectorConfig(
                    options=device_options,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional("phone_number", default=""): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notificare", default=False): BooleanSelector(),
        })
        return self.async_show_form(step_id="registered", data_schema=schema)

    async def async_step_manual(self, user_input=None) -> SubentryFlowResult:
        if user_input is not None:
            name = (user_input.get("custom_name") or "").strip()
            return self.async_create_entry(
                title=name or "Device manuale",
                data={
                    "device_id": None,
                    "custom_name": name,
                    "note": (user_input.get("note") or "").strip() or None,
                    "phone_number": (user_input.get("phone_number") or "").strip() or None,
                    "notifica_sms": user_input.get("notifica_sms", False),
                },
            )

        schema = vol.Schema({
            vol.Required("custom_name"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Optional("note", default=""): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Optional("phone_number", default=""): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notifica_sms", default=False): BooleanSelector(),
        })

        return self.async_show_form(step_id="manual", data_schema=schema)

    async def async_step_reconfigure(self, user_input=None) -> SubentryFlowResult:
        config_entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        is_manual = subentry.data.get("device_id") is None

        if is_manual:
            # Mostra subito il form di riconfigura manuale
            return self.async_show_form(
                step_id="reconfigure_manual",
                data_schema=vol.Schema({
                    vol.Required(
                        "custom_name",
                        default=subentry.data.get("custom_name") or subentry.title,
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                    vol.Optional(
                        "note", default=subentry.data.get("note") or ""
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                    vol.Optional(
                        "phone_number",
                        default=subentry.data.get("phone_number") or "",
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEL)),
                    vol.Optional(
                        "notifica_sms",
                        default=subentry.data.get("notifica_sms", False),
                    ): BooleanSelector(),
                }),
            )

        if user_input is not None:
            return self.async_update_and_abort(
                entry=config_entry,
                subentry=subentry,
                title=subentry.title,
                data_updates={
                    "phone_number": (user_input.get("phone_number") or "").strip() or None,
                    "notificare": user_input.get("notificare", False),
                },
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Optional(
                    "phone_number",
                    default=subentry.data.get("phone_number") or "",
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEL)),
                vol.Optional(
                    "notificare",
                    default=subentry.data.get("notificare", False),
                ): BooleanSelector(),
            }),
        )

    async def async_step_reconfigure_manual(self, user_input=None) -> SubentryFlowResult:
        config_entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()

        if user_input is not None:
            name = (user_input.get("custom_name") or "").strip()
            return self.async_update_and_abort(
                entry=config_entry,
                subentry=subentry,
                title=name or subentry.title,
                data_updates={
                    "custom_name": name,
                    "note": (user_input.get("note") or "").strip() or None,
                    "phone_number": (user_input.get("phone_number") or "").strip() or None,
                    "notifica_sms": user_input.get("notifica_sms", False),
                },
            )

        return self.async_show_form(
            step_id="reconfigure_manual",
            data_schema=vol.Schema({
                vol.Required(
                    "custom_name",
                    default=subentry.data.get("custom_name") or subentry.title,
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Optional(
                    "note", default=subentry.data.get("note") or ""
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Optional(
                    "phone_number",
                    default=subentry.data.get("phone_number") or "",
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEL)),
                vol.Optional(
                    "notifica_sms",
                    default=subentry.data.get("notifica_sms", False),
                ): BooleanSelector(),
            }),
        )



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
        return {"device": DeviceSubentryFlowHandler}


class DeviceSubentryFlowHandler(ConfigSubentryFlow):

    async def async_step_user(self, user_input=None) -> SubentryFlowResult:
        device_registry = dr.async_get(self.hass)
        mobile_devices = [
            d for d in device_registry.devices.values()
            if any(ident[0] == "mobile_app" for ident in d.identifiers)
        ]

        # Escludi device già configurati
        config_entry = self._get_entry()
        configured_ids = {
            sub.data["device_id"]
            for sub in config_entry.subentries.values()
            if "device_id" in sub.data
        }
        available = [d for d in mobile_devices if d.id not in configured_ids]

        if not available:
            return self.async_abort(reason="no_devices_available")

        device_options = {
            d.id: d.name or d.name_by_user or "Dispositivo sconosciuto"
            for d in sorted(available, key=lambda d: d.name or "")
        }

        if user_input is not None:
            device_id = user_input["device_id"]
            device = device_registry.devices.get(device_id)
            return self.async_create_entry(
                title=device.name if device else device_id,
                data={
                    "device_id": device_id,
                    "phone_number": (user_input.get("phone_number") or "").strip() or None,
                    "notificare": user_input.get("notificare", False),
                },
            )

        schema = vol.Schema({
            vol.Required("device_id"): SelectSelector(
                SelectSelectorConfig(
                    options=[{"value": k, "label": v} for k, v in device_options.items()],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional("phone_number", default=""): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional("notificare", default=False): BooleanSelector(),
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_reconfigure(self, user_input=None) -> SubentryFlowResult:
        config_entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()

        if user_input is not None:
            return self.async_update_and_abort(
                entry=config_entry,
                subentry=subentry,
                title=subentry.title,
                data_updates={
                    "phone_number": (user_input.get("phone_number") or "").strip() or None,
                    "notificare": user_input.get("notificare", False),
                },
            )

        schema = vol.Schema({
            vol.Optional(
                "phone_number",
                default=subentry.data.get("phone_number") or "",
            ): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEL)
            ),
            vol.Optional(
                "notificare",
                default=subentry.data.get("notificare", False),
            ): BooleanSelector(),
        })

        return self.async_show_form(step_id="reconfigure", data_schema=schema)
