from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .camera_io import PanasonicCamera

DOMAIN = "panasonic_camera"

class PanasonicCameraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            try:
                # Test camera connection
                camera = PanasonicCamera(
                    user_input["ip"],
                    username=user_input["username"],
                    password=user_input["password"]
                )
                
                if not await camera._test_connection():
                    errors["base"] = "cannot_connect"
                else:
                    # Create unique ID for this camera
                    unique_id = f"panasonic_camera_{user_input['ip']}"

                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Camera {user_input['ip']}",
                        data=user_input
                    )

            except Exception:
                errors["base"] = "connection_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip"): str,
                vol.Required("username", default="Admin"): str,
                vol.Required("password"): str,
                vol.Optional("scan_interval", default=10): int,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PanasonicCameraOptionsFlow(config_entry)

class PanasonicCameraOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 10)
                ): int,
            })
        )
