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
import pdb
import traceback

#append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from lib import omegaWorker

thisusr = decky.USER
thisusrhome = decky.DECKY_USER_HOME

class ConnectionFailedError(Exception):
	#decky.logger.info("Connection could not be established, try again")
	pass

class InvalidIPException(Exception):
	pass

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
				#omegaWorker.WorkerClass().ReconnectProtocol()
				subprocess.run(shlex.split("podman restart xivomega"),check=True,capture_output=True)
				subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
				subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)
				#omegaWorker.WorkerClass().ClearNetavarkRules()
				omegaWorker.WorkerClass().SetRoutes(rt14)
		except subprocess.CalledProcessError as e:
			decky.logger.info("Retrying Connection...")
			ctx = ctx + 1
			#omegaWorker.WorkerClass().ReconnectProtocol()
			subprocess.run(shlex.split("podman restart xivomega"),check=True,capture_output=True)
			subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
			subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)
			#omegaWorker.WorkerClass().ClearNetavarkRules()
			omegaWorker.WorkerClass().SetRoutes(rt14)
			pass
	return ctx

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
			omegaWorker.WorkerClass().stopPodman()
		Plugin._enabled = check['checkd']

	#mitigator method
	async def mitigate(self):
		await asyncio.sleep(5)
		ctx = 1
		while True:
			try:
				if Plugin._enabled:
					decky.logger.info("Plugin is enabled")
					#check if running and if not then start
					isRunning = omegaWorker.WorkerClass.isRunning()
					decky.logger.info("Is xivomega up??: " + str(isRunning)) 
					if isRunning == False:
						decky.logger.info("Activation signal received, starting")
						omegaWorker.WorkerClass.startPodman()
					else: 
						decky.logger.info("Container started - set routes and connect")
					omegaWorker.WorkerClass().SetRoutes(roadsto14)
					ctx = establishConnection(self,roadsto14) 
					decky.logger.info(ctx)
					if ctx == 0:
						omega = f"podman exec -i xivomega /home/omega_alpha.sh"
						#xivomega = Popen(shlex.split(omega), stdin=PIPE, stdout=PIPE, stderr=STDOUT, text=True)
						xivomega = await asyncio.create_subprocess_exec(*shlex.split(omega), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
						# for ln in xivomega.stdout:
						# 	decky.logger.info(ln)
						# 	await asyncio.sleep(0.5)
						while True:
							try:
								Plugin._enabled = True
								ln = await asyncio.wait_for(xivomega.stdout.readline(),1)
								if ln:
									decky.logger.info(ln.decode('utf-8').strip())
									await asyncio.sleep(0.5)
							except asyncio.TimeoutError:
								await asyncio.sleep(0.5)
								pass			
					else:
						raise ConnectionFailedError
						pass
				# else:
				# 	decky.logger.info("Waiting for activation")
			except Exception as e:
				decky.logger.info("Failure on process")
				decky.logger.info(traceback.format_exc())
				pass
			await asyncio.sleep(0.5)


	#function for onKill
	async def stop_status(self):
		Plugin._enabled = False
		decky.logger.info("Killing on the way out")

	# Asyncio-compatible long-running code, executed in a task when the plugin is loaded
	async def _main(self):
		# Omega Code will go here 
		# BIG FYI - Decky uses /usr/bin/podman!!! have this in mind in case something needs fixing or anything
		#network preparations
		#get IP address with cidr from wlan0 only - eth0 en ens* not supported yet
		ipv4 = os.popen('ip addr show wlan0').read().split("inet ")[1].split(" brd")[0] 
		ipv4n, netb = ipv4.split('/')
		subn = ipaddress.ip_network(cidr_to_netmask(ipv4)[0]+'/'+cidr_to_netmask(ipv4)[1], strict=False)
		sdgway = '.'.join(ipv4n.split('.')[:3]) + ".1"
		sdsubn = str(subn.network_address) + "/" + netb
		#get first and last ips from current network 
		#fip is the gateway
		#vip is the ipvlan host adapter - penultimate IP from network
		#lip is the ipvlan from podman - last ip address
		nt = ipaddress.IPv4Network(sdsubn)
		fip = str(nt[1])
		vip = str(nt[-4])
		lip = str(nt[-3])
		brd = str(nt.broadcast_address)
		decky.logger.info("Starting main program")
		decky.logger.info(thisusr)
		decky.logger.info(thisusrhome)
		decky.logger.info(f"Host IPVlan IP: {vip}")
		decky.logger.info(f"Podman IPVlan IP: {lip}")
		decky.logger.info(f"Gateway IP: {fip}")
		#create network and container
		omegaWorker.WorkerClass().CreateHostAdapter(vip,netb,brd)
		omegaWorker.WorkerClass().createIpVlanC(sdsubn,sdgway)
		omegaWorker.WorkerClass().SelfCreateProtocol(lip)
		#omegaWorker.WorkerClass().connectIpVlanC(lip)
		#main loop - it works!!
		try:
			loop = asyncio.get_event_loop()
			Plugin._runner_task = loop.create_task(Plugin.mitigate(self))
			decky.logger.info("Mitigation initiated")
		except Exception:
			decky.logger.exception("main")
			decky.logger.info(pdb.post_mortem())
		except ConnectionFailedError:
			decky.logger.info("Connection Failed")

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
		omegaWorker.WorkerClass.SelfDestructProtocol(roadsto14)
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
