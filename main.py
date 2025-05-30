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
import random
from random import sample
#logger methods based on MagicPods
import logging
from logging.handlers import RotatingFileHandler
import configparser
from configparser import ConfigParser
#append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from lib import omegaWorker
from scapy.all import ARP, Ether, srp


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

CNroads = [
	"109.244.0.0/16",
	"27.221.0.0/16",
	"119.97.0.0/16",
	"162.14.0.0/16"]

JProads = [
	"119.252.36.0/24",
	"119.252.37.0/24",
	"153.254.80.0/24",
	"204.2.29.0/24", 
	"80.239.145.0/24"]

KRroads = ["183.111.189.0/24"]

NNroads = ["124.150.157.0/24","202.67.52.0/24"]

legacyroads = [
	"124.150.157.0/24",
	"153.254.80.0/24",
	"202.67.52.0/24",
	"204.2.29.0/24",
	"80.239.145.0/24"]


roadsto14 = legacyroads

#custom logger - copying implementation form MagicPods - to easily check log

# Create a logger
lvl = logging.DEBUG
_logger = logging.getLogger("magicpods")
_logger.setLevel(lvl)

# Create a file handler and set the level to DEBUG
file_handler = RotatingFileHandler(os.path.join(decky.DECKY_PLUGIN_LOG_DIR,"xivomegalog.txt"), mode='a', maxBytes=5*1024*1024, backupCount=0)
file_handler.setLevel(lvl)

# Create a console handler and set the level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(lvl)

# Create a formatter and set it to the handlers
formatter = logging.Formatter('%(asctime)s  %(levelname)-5s  %(tag)s    %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
_logger.addHandler(file_handler)
_logger.addHandler(console_handler)

logger = logging.LoggerAdapter(_logger, {"tag": "py"})

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

#scapy methods to get network info - get all IPs in use
def scan(ip):
	arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
	result = srp(arp_request, timeout=1, verbose=False)[0]
	devices = [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]
	return devices

def get_device_names(devices):
	device_names = []
	for device in devices:
		try:
			host_name, _, _ = socket.gethostbyaddr(device['ip'])
			device_names.append({'ip': device['ip'], 'mac': device['mac'], 'name': host_name})
		except socket.herror:
		   
			device_names.append({'ip': device['ip'], 'mac': device['mac'], 'name': 'Unknown'})
	return device_names

def get_vip_lip(ipaddr,subnaddr):
	ips = []
	target_ip = ipaddr
	devices_list = scan(target_ip)
	for device in devices_list:
		for k,v in device.items():
			if k in 'ip':
				ips.append(device[k])
	devices_with_names = get_device_names(devices_list)
	
	logger.info("IPs in use:")
	for uip in ips:
		logger.info(uip)
	allip = [str(ip) for ip in ipaddress.IPv4Network(subnaddr)]
	useable_ip = allip[3:-2]
	# Removing elements present in other list
	# using list comprehension
	res = [i for i in useable_ip if i not in ips]
	logger.info("Chosen IPs:")
	vip, lip = sample(res,2)
	logger.info(f"VlanIP: {vip}")
	logger.info(f"Last IP: {lip}")
	return vip, lip

#end of scapy methods

def establishConnection(self,rt14)->int:
	ctx = 1
	logger.info("Establishing network connection...")
	while(5 > ctx > 0):
		try:
			dice = Popen(shlex.split("podman exec -i xivomega ping 204.2.29.7 -c 5"),stdin=PIPE,stdout=PIPE,stderr=STDOUT)
			dice.wait()
			if dice.returncode == 0:
				logger.info("Network Established")
				ctx = 0
			else:
				logger.info("Retrying Connection..")
				ctx = ctx + 1
				omegaWorker.WorkerClass().ReconnectProtocol()
				omegaWorker.WorkerClass().SetRoutes(rt14)
		except subprocess.CalledProcessError as e:
			logger.info("Retrying Connection...")
			ctx = ctx + 1
			omegaWorker.WorkerClass().ReconnectProtocol()
			omegaWorker.WorkerClass().SetRoutes(rt14)
			pass
	return ctx

def networkSetup(self):
	netwElems = {}
	this_dev = omegaWorker.WorkerClass().get_current_device()
	logger.info(f"Device under use: {this_dev}")
	ipv4 = os.popen('ip addr show ' + this_dev).read().split("inet ")[1].split(" brd")[0] 
	ipv4n, netb = ipv4.split('/')
	subn = ipaddress.ip_network(cidr_to_netmask(ipv4)[0]+'/'+cidr_to_netmask(ipv4)[1], strict=False)
	sdgway = '.'.join(ipv4n.split('.')[:3]) + ".1"
	sdsubn = str(subn.network_address) + "/" + netb
	nt = ipaddress.IPv4Network(sdsubn)
	#get vip and lip frpm random method - this way no config is needed
	fip = str(nt[1])
	#vip = str(nt[-4])
	#lip = str(nt[-3])
	vip, lip = get_vip_lip(ipv4n,sdsubn)
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

	#read log
	async def read_logs(self):
		output = ""
		with open(os.path.join(decky.DECKY_PLUGIN_LOG_DIR, "xivomegalog.txt")) as file:
			for line in (file.readlines() [-150:]):
				output += line
		return output
	
	# Current Status
	async def curr_status(self)-> bool:
		logger.info(Plugin._enabled)
		return Plugin._enabled

	#switch toggle status
	async def toggle_status(self, check):
		logger.info(check['checkd'])
		logger.info(type(check['checkd']))
		if Plugin._enabled == True and check['checkd'] == False:
			logger.info("Disabling XIVOmega")
			omegaWorker.WorkerClass().stopPodman()
			omegaWorker.WorkerClass().SelfDisableProtocol()
		await decky.emit("turnToggleOn")
		Plugin._enabled = check['checkd']
	
	#get opcodes from front end
	async def use_cust_opcodes(self, 
		use_custom_opcodes:bool, 
		C2S_ActionRequest:str, 
		C2S_ActionRequestGroundTargeted:str, 
		S2C_ActionEffect01:str, 
		S2C_ActionEffect08:str, 
		S2C_ActionEffect16:str, 
		S2C_ActionEffect24:str, 
		S2C_ActionEffect32:str, 
		S2C_ActorCast:str, 
		S2C_ActorControl:str,
		S2C_ActorControlSelf:str):
		op_parms = {
			'use_custom_opcodes':use_custom_opcodes,
        	'C2S_ActionRequest':C2S_ActionRequest,
        	'C2S_ActionRequestGroundTargeted':C2S_ActionRequestGroundTargeted,
        	'S2C_ActionEffect01':S2C_ActionEffect01,
        	'S2C_ActionEffect08':S2C_ActionEffect08,
        	'S2C_ActionEffect16':S2C_ActionEffect16,
        	'S2C_ActionEffect24':S2C_ActionEffect24,
        	'S2C_ActionEffect32':S2C_ActionEffect32,
        	'S2C_ActorCast':S2C_ActorCast,
        	'S2C_ActorControl':S2C_ActorControl,
        	'S2C_ActorControlSelf':S2C_ActorControlSelf
			}
		logger.info(f'Custom Opcodes: ' + str(op_parms['use_custom_opcodes']))
		new_opcode_conf = ConfigParser()
		new_opcode_conf["Opcodes"] = {
			"use_custom_opcodes": op_parms['use_custom_opcodes'],
			"C2S_ActionRequest": op_parms['C2S_ActionRequest'],
			"C2S_ActionRequestGroundTargeted": op_parms['C2S_ActionRequestGroundTargeted'],
			"S2C_ActionEffect01": op_parms['S2C_ActionEffect01'],
			"S2C_ActionEffect08": op_parms['S2C_ActionEffect08'],
			"S2C_ActionEffect16": op_parms['S2C_ActionEffect16'],
			"S2C_ActionEffect24": op_parms['S2C_ActionEffect24'],
			"S2C_ActionEffect32": op_parms['S2C_ActionEffect32'],
			"S2C_ActorCast": op_parms['S2C_ActorCast'],
			"S2C_ActorControl": op_parms['S2C_ActorControl'],
			"S2C_ActorControlSelf": op_parms['S2C_ActorControlSelf']
		}
		try:
			with open(os.path.join(pluginpath,'podman_config','opcode_conf.ini'),'w') as conf:
				new_opcode_conf.write(conf)
				if op_parms['use_custom_opcodes']:
					logger.info("New opcode configuration saved. To be applied on next mitigator start")
				else:
					logger.info("Reverting to Default Opcodes on next mitigation restart")
		except Exception as e:
			logger.error(traceback.format_exc())

	#mitigator method
	async def mitigate(self):
		await asyncio.sleep(5)
		ctx = 1
		while True:
			try:
				if Plugin._enabled:
					await decky.emit("turnToggleOff")
					logger.info("XIVOmega is enabled")
					isRunning = omegaWorker.WorkerClass.isRunning()
					if isRunning == False:
						logger.info("Activation signal received, starting new container and network config")
						netw = networkSetup(self)
						omegaWorker.WorkerClass().CreateHostAdapter(netw["vip"],netw["netb"],netw["brd"])
						omegaWorker.WorkerClass().createIpVlanC(netw["sdsubn"],netw["sdgway"])
						#check opcode_config_file
						omegaWorker.WorkerClass().SelfCreateProtocol(netw["lip"])
					else: 
						logger.info("Container started - set routes and connect")
					omegaWorker.WorkerClass().SetRoutes(roadsto14)
					ctx = establishConnection(self,roadsto14) 
					#check if custom opcode is in use - front end stuff should be here I think
					omegaWorker.WorkerClass().opcode_config(pluginpath)
					if ctx == 0:
						await decky.emit("turnToggleOn")
						omega = f"podman exec -i xivomega /home/omega_alpha.sh"
						xivomega = await asyncio.create_subprocess_exec(*shlex.split(omega), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
						await decky.emit("clearStorage")
						while True:
							try:
								if Plugin._enabled:
									await decky.emit("Vlan_IP",str(netw["vip"]))
									ln = await asyncio.wait_for(xivomega.stdout.readline(),1)
									if ln:
										logger.info(ln.decode('utf-8').strip())
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
				logger.info("Failure on process")
				logger.info(traceback.format_exc())
				await decky.emit("turnToggleOn")
				await decky.emit("clearStorage")
				pass
			await asyncio.sleep(0.5)

	#function for onKill
	async def stop_status(self):
		Plugin._enabled = False
		logger.info("Killing on the way out")

	# Asyncio-compatible long-running code, executed in a task when the plugin is loaded
	async def _main(self):
		# BIG FYI - Decky uses /usr/bin/podman!!! have this in mind in case something needs fixing or anything
		# await decky.emit('purgeStorage')
		logger.info(f"Python Version used by Decky: {sys.version}")
		logger.info(f"Python Route: {sys.executable}")
		omegaWorker.WorkerClass.SelfCleaningProtocol()
		# check if podman storage is patched
		logger.info(xivomega_storage)
		confCheck = omegaWorker.WorkerClass.checkPodmanConf(pluginpath)
		if confCheck >= 0: 
			storageCheck = omegaWorker.WorkerClass.checkPodmanStorage()
			if storageCheck:
				logger.info("Initiating storage.conf patching process")
				omegaWorker.WorkerClass().fixPodmanStorage(xivomega_storage)
		else:
			raise StorageConfSetupError
		#network preparations
		#get IP address with cidr from wlan0 only - eth0 and ens* connections not supported yet
		#wait for 15 seconds before scanning for IP - 
		await asyncio.sleep(15)
		try:
			netw = networkSetup(self)
			logger.info("Starting main program")
			logger.info(f"Network Interface in use: " + omegaWorker.WorkerClass().get_current_device())
			logger.info(f"Host IPVlan IP: " + str(netw["vip"]))
			logger.info(f"Podman IPVlan IP: " + str(netw["lip"]))
			logger.info(f"Gateway IP: " + str(netw["fip"]))
			#send IPVlan host info to the UI - this will be the new Deck IP while the plugin is in use
			await decky.emit("Vlan_IP",str(netw["vip"]))
		except IndexError:
			logger.info("wlan0 couldn't be found connected")
			await decky.emit("wlan0ConnError")
		#main loop
		try:
			loop = asyncio.get_event_loop()
			Plugin._runner_task = loop.create_task(Plugin.mitigate(self))
			logger.info("Mitigation Protocol Initiated")
		except Exception:
			logger.exception("main")
			pass
		except ConnectionFailedError:
			logger.info("Connection Failed")
			await decky.emit("connectionErrPrompt")
		except StorageConfSetupError:
			logger.info("Storage.conf file could not be copied.")
			await decky.emit("storageConfErrPromt")

	# Function called first during the unload process, utilize this to handle your plugin being stopped, but not
	# completely removed
	async def _unload(self):
		Plugin.stop_status(self)
		# await decky.emit('purgeStorage')
		omegaWorker.WorkerClass.SelfDestructProtocol(roadsto14)
		logger.info("Goodnight World!")
		pass

	# Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
	# plugin that may remain on the system
	async def _uninstall(self):
		omegaWorker.WorkerClass.SelfDestructProtocol(roadsto14)
		omegaWorker.WorkerClass.restorePodmanStorage(xivomega_storage,pluginpath)
		logger.info("Goodbye World!")
		pass

	# # Migrations that should be performed before entering `_main()`.
	# async def _migration(self):
	# 	logger.info("Migrating")
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
