from pathlib import Path
import subprocess
import sys
import os
import asyncio
import decky

class Plugin:

    _enabled = False

    # Current Status
    async def curr_status(self)-> bool:
        decky.logger.info("Informing Status")
        return Plugin._enabled

    #switch toggle status
    async def toggle_status(self, check):
        decky.logger.info(check)
        decky.logger.info(type(check))
        if Plugin._enabled == True and check == False:
            decky.logger.info("Switched via toggle_status")
        Plugin._enabled = check
    
    #function for onKill
    async def stop_status(self):
        Plugin._enabled = False
        decky.logger.info("Killing on the way out")


    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        # Omega Code will go here 
        # ToDo: 
        # Copy container storage into home folder under xivomega_cont 
        # Modify /etc/containers/storage.conf 
        # create ipvlan and podman ipvlan network
        # create container 
        decky.logger.info("Entering inside main")

    # Enable services
    # async def enable(self):
    #     Plugin._enabled = True

    # Disable services
    # async def disable(self):
    #     Plugin._enabled = False

        # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self):
        Plugin.stop_status(self)
        decky.logger.info("Goodnight World!")
        pass

    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self):
        decky.logger.info("Goodbye World!")
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky.DECKY_PLUGIN_LOG_DIR/template.log`
        decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky.DECKY_PLUGIN_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.DECKY_PLUGIN_SETTINGS_DIR/`
        decky.migrate_settings(
            os.path.join(decky.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky.DECKY_PLUGIN_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.DECKY_PLUGIN_RUNTIME_DIR/`
        decky.migrate_runtime(
            os.path.join(decky.DECKY_HOME, "template"),
            os.path.join(decky.DECKY_USER_HOME, ".local", "share", "decky-template"))
