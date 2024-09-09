import os
import subprocess

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky

logger = decky_plugin.logger

class Plugin:
    _enabled = False

    async def is_enabled(self):
        return Plugin._enabled

    async def set_enabled(self, enabled):
        logger.info(enabled)
        logger.info(type(enabled)) 
        if Plugin._enabled == True and enabled == False:
            ret = subprocess.run(shlex.split("podman stop xivtest"))
        Plugin._enabled = enabled

    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    async def podmanToggleTest(self,togState):
        rc = 0
        if(togState==True):
            try:
                hworld = subprocess.run(shlex.split("podman start xivtest"),check=True,capture_output=True)
                if hworld.returncode == 0:
				    #print("XIVOmega says - Hello World")
                    rc = 1
            except subprocess.CalledProcessError as e:
                rc = -4
        else:
            try:
                hworld = subprocess.run(shlex.split("podman stop xivtest"),check=True,capture_output=True)
                if hworld.returncode == 0:
			        #print("XIVOmega says - Hello World")
                    rc = 2
            except subprocess.CalledProcessError as e:
                rc = -5
        return togState

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        decky_plugin.logger.info("Hello World!")

    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self):
        decky_plugin.logger.info("Goodnight World!")
        pass

    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self):
        decky_plugin.logger.info("Goodbye World!")
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/template.log`
        decky_plugin.migrate_logs(os.path.join(decky_plugin.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
        decky_plugin.migrate_settings(
            os.path.join(decky_plugin.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        decky_plugin.migrate_runtime(
            os.path.join(decky_plugin.DECKY_HOME, "template"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-template"))
