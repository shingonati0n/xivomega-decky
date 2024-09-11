#from Plugin
from pathlib import Path
import subprocess
import sys
import os
import asyncio
import decky
#from original program
import socket
import ipaddress
import struct
import shlex
import time 
import io
import configparser
from subprocess import Popen, PIPE, CalledProcessError
from getpass import getpass

#append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from lib import omegaWorker

thisusr = decky.USER
thisusrhome = decky.DECKY_USER_HOME

#static stuff
roadsto14 = [
	"124.150.157.0/24",
	"153.254.80.0/24",
	"202.67.52.0/24",
	"204.2.29.0/24",
	"80.239.145.0/24"]

#get subnet mask and subnet
def cidr_to_netmask(cidr):
	network, net_bits = cidr.split('/')
	host_bits = 32 - int(net_bits)
	netmask = socket.inet_ntoa(struct.pack('!I',(1 << 32) - (1 << host_bits)))
	return network, netmask

#validate IP Address
def is_valid_ipv4_address(address):
	try:
		socket.inet_pton(socket.AF_INET, address)
	except AttributeError:  # no inet_pton here, sorry
		try:
			socket.inet_aton(address)
		except socket.error:
			return False
		return address.count('.') == 3
	except socket.error:  # not a valid address
		return False
	return True

#Plugin code
class Plugin:

	_enabled = False
	
	# Current Status
	async def curr_status(self)-> bool:
		decky.logger.info(Plugin._enabled)
		return Plugin._enabled

	#switch toggle status
	async def toggle_status(self, check):
		decky.logger.info(check)
		decky.logger.info(type(check))
		if Plugin._enabled == True and check['checkd'] == False:
			decky.logger.info("Switched via toggle_status")
			#omegaBeetle.SelfDestructProtocol()
			omegaBeetle.testStop()
		Plugin._enabled = check['checkd']
	
	#function for onKill
	async def stop_status(self):
		Plugin._enabled = False
		decky.logger.info("Killing on the way out")

	# Asyncio-compatible long-running code, executed in a task when the plugin is loaded
	async def _main(self):
		omegaBeetle = omegaWorker.WorkerClass()
		# try:
		# 	xivomega = subprocess.Popen(str(Path(decky.DECKY_PLUGIN_DIR) / "omega_create.sh"))
		# 	if xivomega.returncode == 0:
		# 		decky.logger.info("podman container created successfully")
		# except subprocess.CalledProcessError as e:
		# 	pass
		# 	decky.logger.info(e.stdout.decode())
		# Omega Code will go here 
		# ToDo: 
		# Copy container storage into home folder under xivomega_cont // add select path for this
		# Modify /etc/containers/storage.conf 
		# create ipvlan and podman ipvlan network
		# create container 
		decky.logger.info("Starting main program")
		decky.logger.info(thisusr)
		decky.logger.info(thisusrhome)
		omegaBeetle.testStart()
		omegaBeetle.podmanInfo()

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
