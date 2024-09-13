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
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
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
		decky.logger.info(check['checkd'])
		decky.logger.info(type(check['checkd']))
		if Plugin._enabled == True and check['checkd'] == False:
			decky.logger.info("Switched via toggle_status")
			#omegaBeetle.SelfDestructProtocol()
			omegaWorker.WorkerClass().testStop()
		Plugin._enabled = check['checkd']

	#mitigator method
	async def mitigate(self):
		await asyncio.sleep(5)
		while True:
			try:
				if Plugin._enabled:
					decky.logger.info("Plugin is enabled")
					#check if running and if not then start
					isRunning = omegaWorker.WorkerClass.isRunning()
					decky.logger.info(isRunning) 
					if isRunning == False:
						decky.logger.info("Activation signal received, starting it")
						omegaWorker.WorkerClass.testStart()
					#omega = f"podman exec -i xivomega /home/omega_alpha.sh"
					omega = f"podman exec xivtest ping 192.168.100.82"
					xivomega = Popen(shlex.split(omega), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
					for ln in xivomega.stdout:
						decky.logger.info(ln)
						await asyncio.sleep(0.5)
				else:
					decky.logger.info("Waiting for activation")
			except Exception:
				decky.logger.info("failure on process")
				decky.logger.info(xivomega.stderr.decode())
			await asyncio.sleep(0.5)


	#function for onKill
	async def stop_status(self):
		Plugin._enabled = False
		decky.logger.info("Killing on the way out")

	# Asyncio-compatible long-running code, executed in a task when the plugin is loaded
	async def _main(self):
		# Omega Code will go here 
		# BIG FYI - Decky uses /usr/bin/podman!!! have this in mind in case something needs fixing or anything
		# ToDo // does it run forever??: 
		#Pre process when launchng plugin
		# Copy container storage into home folder under xivomega_cont // add select path for this // NO 
		# Modify /etc/containers/storage.conf  // NO
		# create container // NO
		# create ipvlan (host and container)
		# connect to ipvlan // NO 
		# set iptables // NO
		# ping game // NO 
		# run mitigator // YES -- this has to be inside create_task -- 
		decky.logger.info("Starting main program")
		decky.logger.info(thisusr)
		decky.logger.info(thisusrhome)
		omegaBeetle = omegaWorker.WorkerClass()
		omegaWorker.WorkerClass().testStart()
		#main loop - it works!!
		try:
			loop = asyncio.get_event_loop()
			Plugin._runner_task = loop.create_task(Plugin.mitigate(self))
			decky.logger.info("Mitigation initiated")
		except Exception:
			decky.logger.exception("main")
		#omegaBeetle.testStart()
		#omegaBeetle.podmanInfo()

	#need a way to stop the mitigator and virtually send a ctrl-C
	#restart mitigator when toggled - not the whole preroutine though
	

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
