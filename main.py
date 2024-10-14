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
import io
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from getpass import getpass
import pdb
import traceback

#append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from lib import omegaWorker

thisusr = decky.USER
thisusrhome = decky.DECKY_USER_HOME
xivomega_storage = decky.DECKY_PLUGIN_RUNTIME_DIR
pluginpath = decky.DECKY_PLUGIN_DIR

class ConnectionFailedError(Exception):
	pass

class InvalidIPException(Exception):
	pass

class WifiNotOnError(Exception):
	pass

class StorageConfSetupError(Exception):
	pass

#static stuff
roadsto14 = [
	"124.150.157.0/24",
	"153.254.80.0/24",
	"202.67.52.0/24",
	"204.2.29.0/24",
	"80.239.145.0/24"]

#fix etc/containers/storage.conf to avoid podman no space left issue

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
	except AttributeError:  
		try:
			socket.inet_aton(address)
		except socket.error:
			return False
		return address.count('.') == 3
	except socket.error: 
		return False
	return True

def establishConnection(self,rt14)->int:
	ctx = 1
	decky.logger.info("Establishing network connection...")
	while(5 > ctx > 0):
		try:
			dice = Popen(shlex.split("podman exec -i xivomega ping 204.2.29.7 -c 5"),stdin=PIPE,stdout=PIPE,stderr=STDOUT)
			dice.wait()
			if dice.returncode == 0:
				decky.logger.info("Network Established")
				ctx = 0
			else:
				decky.logger.info("Retrying Connection..")
				ctx = ctx + 1
				omegaWorker.WorkerClass().ReconnectProtocol()
				omegaWorker.WorkerClass().SetRoutes(rt14)
		except subprocess.CalledProcessError as e:
			decky.logger.info("Retrying Connection...")
			ctx = ctx + 1
			omegaWorker.WorkerClass().ReconnectProtocol()
			omegaWorker.WorkerClass().SetRoutes(rt14)
			pass
	return ctx

def networkSetup(self):
	netwElems = {}
	ipv4 = os.popen('ip addr show wlan0').read().split("inet ")[1].split(" brd")[0] 
	ipv4n, netb = ipv4.split('/')
	subn = ipaddress.ip_network(cidr_to_netmask(ipv4)[0]+'/'+cidr_to_netmask(ipv4)[1], strict=False)
	sdgway = '.'.join(ipv4n.split('.')[:3]) + ".1"
	sdsubn = str(subn.network_address) + "/" + netb
	nt = ipaddress.IPv4Network(sdsubn)
	fip = str(nt[1])
	vip = str(nt[-4])
	lip = str(nt[-3])
	brd = str(nt.broadcast_address)
	netwElems["ipv4"] = ipv4
	netwElems["ipv4n"] = ipv4n
	netwElems["netb"] = netb
	netwElems["subn"] = subn
	netwElems["sdgway"] = sdgway
	netwElems["sdsubn"] = sdsubn
	netwElems["nt"] = nt
	netwElems["fip"] = fip
	netwElems["vip"] = vip
	netwElems["lip"] = lip 
	netwElems["brd"] = brd 
	return netwElems

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
			decky.logger.info("Disabling XIVOmega")
			omegaWorker.WorkerClass().stopPodman()
			omegaWorker.WorkerClass().SelfDisableProtocol()
		await decky.emit("turnToggleOn")
		Plugin._enabled = check['checkd']

	#mitigator method
	async def mitigate(self):
		await asyncio.sleep(5)
		ctx = 1
		while True:
			try:
				if Plugin._enabled:
					await decky.emit("turnToggleOff")
					decky.logger.info("XIVOmega is enabled")
					isRunning = omegaWorker.WorkerClass.isRunning()
					if isRunning == False:
						decky.logger.info("Activation signal received, starting new container and network config")
						netw = networkSetup(self)
						omegaWorker.WorkerClass().CreateHostAdapter(netw["vip"],netw["netb"],netw["brd"])
						omegaWorker.WorkerClass().createIpVlanC(netw["sdsubn"],netw["sdgway"])
						omegaWorker.WorkerClass().SelfCreateProtocol(netw["lip"])
					else: 
						decky.logger.info("Container started - set routes and connect")
					omegaWorker.WorkerClass().SetRoutes(roadsto14)
					ctx = establishConnection(self,roadsto14) 
					if ctx == 0:
						await decky.emit("turnToggleOn")
						omega = f"podman exec -i xivomega /home/omega_alpha.sh"
						xivomega = await asyncio.create_subprocess_exec(*shlex.split(omega), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
						while True:
							try:
								if Plugin._enabled:
									ln = await asyncio.wait_for(xivomega.stdout.readline(),1)
									if ln:
										decky.logger.info(ln.decode('utf-8').strip())
										await asyncio.sleep(0.5)
								else:
									break
							except asyncio.TimeoutError:
								await asyncio.sleep(0.5)
								if not Plugin._enabled:
									break
								pass			
					else:
						raise ConnectionFailedError
						await decky.emit("turnToggleOn")
						pass
			except Exception as e:
				decky.logger.info("Failure on process")
				decky.logger.info(traceback.format_exc())
				await decky.emit("turnToggleOn")
				pass
			await asyncio.sleep(0.5)

	#function for onKill
	async def stop_status(self):
		Plugin._enabled = False
		decky.logger.info("Killing on the way out")

	# Asyncio-compatible long-running code, executed in a task when the plugin is loaded
	async def _main(self):
		# BIG FYI - Decky uses /usr/bin/podman!!! have this in mind in case something needs fixing or anything
		omegaWorker.WorkerClass.SelfCleaningProtocol()
		# check if podman storage is patched
		decky.logger.info(xivomega_storage)
		confCheck = omegaWorker.WorkerClass.checkPodmanConf(pluginpath)
		if confCheck >= 0: 
			storageCheck = omegaWorker.WorkerClass.checkPodmanStorage()
			if storageCheck:
				decky.logger.info("Initiating storage.conf patching process")
				omegaWorker.WorkerClass().fixPodmanStorage(xivomega_storage)
		else:
			raise StorageConfSetupError
		#network preparations
		#get IP address with cidr from wlan0 only - eth0 and ens* connections not supported yet
		#wait for 15 seconds before scanning for IP - 
		await asyncio.sleep(15)
		try:
			netw = networkSetup(self)
			decky.logger.info("Starting main program")
			decky.logger.info(f"Host IPVlan IP: " + str(netw["vip"]))
			decky.logger.info(f"Podman IPVlan IP: " + str(netw["lip"]))
			decky.logger.info(f"Gateway IP: " + str(netw["fip"]))
		except IndexError:
			decky.logger.info("wlan0 couldn't be found connected")
			await decky.emit("wlan0ConnError")
		#main loop
		try:
			loop = asyncio.get_event_loop()
			Plugin._runner_task = loop.create_task(Plugin.mitigate(self))
			decky.logger.info("Mitigation Protocol Initiated")
		except Exception:
			decky.logger.exception("main")
			pass
		except ConnectionFailedError:
			decky.logger.info("Connection Failed")
			await decky.emit("connectionErrPrompt")
		except StorageConfSetupError:
			decky.logger.info("Storage.conf file could not be copied.")
			await decky.emit("storageConfErrPromt")

	# Function called first during the unload process, utilize this to handle your plugin being stopped, but not
	# completely removed
	async def _unload(self):
		Plugin.stop_status(self)
		omegaWorker.WorkerClass.SelfDestructProtocol(roadsto14)
		decky.logger.info("Goodnight World!")
		pass

	# Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
	# plugin that may remain on the system
	async def _uninstall(self):
		omegaWorker.WorkerClass.SelfDestructProtocol(roadsto14)
		omegaWorker.WorkerClass.restorePodmanStorage(xivomega_storage,pluginpath)
		decky.logger.info("Goodbye World!")
		pass

	# # Migrations that should be performed before entering `_main()`.
	# async def _migration(self):
	# 	decky.logger.info("Migrating")
	# 	# Here's a migration example for logs:
	# 	# - `~/.config/decky-template/template.log` will be migrated to `decky.DECKY_PLUGIN_LOG_DIR/template.log`
	# 	decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
	# 										   ".config", "decky-template", "template.log"))
	# 	# Here's a migration example for settings:
	# 	# - `~/homebrew/settings/template.json` is migrated to `decky.DECKY_PLUGIN_SETTINGS_DIR/template.json`
	# 	# - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.DECKY_PLUGIN_SETTINGS_DIR/`
	# 	decky.migrate_settings(
	# 		os.path.join(decky.DECKY_HOME, "settings", "template.json"),
	# 		os.path.join(decky.DECKY_USER_HOME, ".config", "decky-template"))
	# 	# Here's a migration example for runtime data:
	# 	# - `~/homebrew/template/` all files and directories under this root are migrated to `decky.DECKY_PLUGIN_RUNTIME_DIR/`
	# 	# - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.DECKY_PLUGIN_RUNTIME_DIR/`
	# 	decky.migrate_runtime(
	# 		os.path.join(decky.DECKY_HOME, "template"),
	# 		os.path.join(decky.DECKY_USER_HOME, ".local", "share", "decky-template"))
