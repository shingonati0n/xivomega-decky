#from Plugin
from pathlib import Path
import subprocess
import sys
import os
import decky
#from original program
import socket
import ipaddress
import struct
import shlex
import io
from subprocess import Popen, PIPE, CalledProcessError, STDOUT

class WorkerClass:
	@staticmethod
	def SelfCreateProtocol(lip):
		omegapod = f"""podman create \
		  --replace \
		  --name=xivomega \
		  --ip=10.88.0.7 \
		  --sysctl net.ipv4.ip_forward=1 \
		  --sysctl net.ipv4.conf.all.route_localnet=1 \
		  --net=podman \
		  --cap-add=NET_RAW,NET_ADMIN \
		  -i quay.io/shingonati0n/xivomega:latest /bin/sh"""
		try:
			xivomega = subprocess.run(shlex.split(omegapod),check=True,capture_output=True)
			if xivomega.returncode == 0:
				decky.logger.info("podman container created successfully")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		
		hclosew = f"podman network connect xivlanc xivomega --ip={lip}"
		try:
			hclosew = subprocess.run(shlex.split(hclosew),check=True,capture_output=True)
			if hclosew.returncode == 0:
				decky.logger.info("hooked to podman ipvlan network")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		try:
			hworld = subprocess.run(shlex.split("podman start xivomega"),check=True,capture_output=True)
			if hworld.returncode == 0:
				decky.logger.info("XIVOmega says - Hello World")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def createIpVlanC(sdsubn,sdgway):
		podnet = f"podman network create --subnet={sdsubn} --gateway={sdgway} --driver=ipvlan -o parent=wlan0 xivlanc"
		try:
			xivnet = subprocess.run(shlex.split(podnet),check=True,capture_output=True)
			if xivnet.returncode == 0:
				decky.logger.info("podman ipvlan network xivlanc has been created")
		except subprocess.CalledProcessError as e: 
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def connectIpVlanC(lip):
		#connect created container to podman ipvlan network - using last IP Address
		hclosew = f"podman network connect xivlanc xivomega --ip={lip}"
		try:
			hclosew = subprocess.run(shlex.split(hclosew),check=True,capture_output=True)
			if hclosew.returncode == 0:
				print("hooked to podman ipvlan network")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
	
	@staticmethod
	def fixPodmanStorage(runpath):
		podstorecmd = f"cp /etc/containers/storage.conf {runpath}/storage.conf.bak"
		psf = subprocess.run(shlex.split(podstorecmd),check=True,capture_output=True)
		try:
		   	if psf.returncode==0:
		   		decky.logger.info("/etc/containers/storage.conf backed up")
		   		pass
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		
		search_text = 'graphroot = "/var/lib/containers/storage"'
		new_text = f'graphroot = "{runpath}"'
		decky.logger.info(search_text)
		decky.logger.info(new_text)

		with open(Path(runpath) / "storage.conf.bak","r") as cfile:
			nfile = cfile.read()
			nfile = nfile.replace(search_text,new_text)
		
		with open(Path(runpath) / "storage_new.conf","w") as ffile:
			ffile.write(nfile)

		pushfix = f"cp {runpath}/storage_new.conf /etc/containers/storage.conf"
		fpush = subprocess.run(shlex.split(pushfix),check=True,capture_output=True)
		try:
			if fpush.returncode==0:
				decky.logger.info("/etc/container/storage.conf has been patched")
				decky.logger.info(f"podman image will be saved to {runpath}")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def restorePodmanStorage(runpath):
		podstorecmd = f"cp {runpath}/storage.conf.bak /etc/containers/storage.conf"
		psf = subprocess.run(shlex.split(podstorecmd),check=True,capture_output=True)
		try:
		   	if psf.returncode==0:
		   		decky.logger.info("original /etc/containers/storage.conf has been restored")
		   		pass
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())


	@staticmethod
	def SetRoutes(rt14):
		for r in rt14:
			way = f"ip route add {r} via 10.88.0.7"
			try:
				nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
				if nav.returncode==0:
		   			decky.logger.info(f"route to {r} added")
			except subprocess.CalledProcessError as e:
				decky.logger.info(e.stderr.decode())
				pass

	@staticmethod
	def ReconnectProtocol():
		subprocess.run(shlex.split("podman restart xivomega"),check=True,capture_output=True)
		subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
		subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)

	@staticmethod
	def CreateHostAdapter(virtual_ip,netbits,broadcast):
		ipvl1 = f"ip link add xivlanh link wlan0 type ipvlan mode l2"
		ipvl2 = f"ip addr add {virtual_ip}/{netbits} brd {broadcast} dev xivlanh"
		ipvl3 = f"ip link set xivlanh up"
		try:
			ipvlh1 = subprocess.run(shlex.split(ipvl1),check=True,capture_output=True)
			if ipvlh1.returncode == 0:
				decky.logger.info("host ipvlan interface created")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		
		try:
			ipvlh2 = subprocess.run(shlex.split(ipvl2),check=True,capture_output=True)
			if ipvlh2.returncode == 0:
				decky.logger.info(f"host ipvlan interface IP is {virtual_ip}")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		
		try:
			ipvlh3 = subprocess.run(shlex.split(ipvl3),check=True,capture_output=True)
			if ipvlh3.returncode == 0:
				decky.logger.info("host ipvlan interface is up")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def SelfDisableProtocol():
		decky.logger.info("Stopping XIVOmega")
		try:
			panto = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if panto.returncode == 0:
				decky.logger.info("XIVOmega Container Stopped")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			atomic = subprocess.run(shlex.split("podman network disconnect xivlanc xivomega"),check=True,capture_output=True)
			if atomic.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Disconnected")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				decky.logger.info("XIVOmega Container removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				decky.logger.info("Host IPVlan turned off")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				decky.logger.info("Host IPVlan removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		decky.logger.info("Awaiting reactivation")

	@staticmethod
	def SelfCleaningProtocol():
		decky.logger.info("Stopping XIVOmega if up")
		try:
			panto = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if panto.returncode == 0:
				decky.logger.info("XIVOmega Container Stopped")
		except subprocess.CalledProcessError as e:
			pass
		try:
			atomic = subprocess.run(shlex.split("podman network disconnect xivlanc xivomega"),check=True,capture_output=True)
			if atomic.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Disconnected")
		except subprocess.CalledProcessError as e:
			pass
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Removed")
		except subprocess.CalledProcessError as e:
			pass
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				decky.logger.info("XIVOmega Container removed")
		except subprocess.CalledProcessError as e:
			pass
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				decky.logger.info("Host IPVlan turned off")
		except subprocess.CalledProcessError as e:
			pass
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				decky.logger.info("Host IPVlan removed")
		except subprocess.CalledProcessError as e:
			pass
		decky.logger.info("Cleanup Completed")

	@staticmethod
	def SelfDestructProtocol(rt14):
		decky.logger.info("Terminating Mitigation Protocol and XIVOmega")
		for r in rt14:
			way = f"ip route del {r} via 10.88.0.7"
			try:
				nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
				if nav.returncode==0:
		   			decky.logger.info(f"route to {r} deleted")
			except subprocess.CalledProcessError as e:
					decky.logger.info(e.stderr.decode())
					pass
		try:
			panto = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if panto.returncode == 0:
				decky.logger.info("XIVOmega Container Stopped")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			atomic = subprocess.run(shlex.split("podman network disconnect xivlanc xivomega"),check=True,capture_output=True)
			if atomic.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Disconnected")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				decky.logger.info("XIVOmega Container removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				decky.logger.info("Host IPVlan turned off")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				decky.logger.info("Host IPVlan removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
			pass
		decky.logger.info("All done - Goodbye")

	@staticmethod
	def isRunning()->bool:
		try:
			rcheck = subprocess.run(shlex.split(r"podman ps -f name=xivomega --format {{.Status}}"),check=True,capture_output=True)
			decky.logger.info(rcheck.stdout.decode())
			if str(rcheck.stdout.decode()[:2]).lower() == "up":
				return True
			else:
				return False
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def startPodman():
		try:
			tworld = subprocess.run(shlex.split("podman start xivomega"),check=True,capture_output=True)
			if tworld.returncode == 0:
				decky.logger.info("podman started successfully")
				decky.logger.info(tworld.stdout.decode())
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def stopPodman():
		try:
			tworld = subprocess.run(shlex.split("podman kill --signal INT xivomega"),check=True,capture_output=True)
			if tworld.returncode == 0:
				decky.logger.info("podman execution halted")
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
		try:
			sworld = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if sworld.returncode == 0:
				decky.logger.info("podman stopped successfully")
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())

#testMethods - these will be static
	@staticmethod
	def testStart():
		try:
			tworld = subprocess.run(shlex.split("podman start xivtest"),check=True,capture_output=True)
			if tworld.returncode == 0:
				decky.logger.info("podman started successfully")
				decky.logger.info(tworld.stdout.decode())
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
	@staticmethod					
	def podmanInfo():
		try:
			pworld = subprocess.run(shlex.split("podman container ls -a"),check=True,capture_output=True)
			nworld = subprocess.run(shlex.split("podman inspect xivtest"),check=True,capture_output=True)
			if pworld.returncode == 0:
				decky.logger.info(pworld.stdout.decode())
			if nworld.returncode == 0:
				decky.logger.info(nworld.stdout.decode())
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())

	@staticmethod
	def testStop():
		try:
			tworld = subprocess.run(shlex.split("podman kill --signal INT xivtest"),check=True,capture_output=True)
			if tworld.returncode == 0:
				decky.logger.info("podman execution halted")
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
		try:
			sworld = subprocess.run(shlex.split("podman stop xivtest"),check=True,capture_output=True)
			if sworld.returncode == 0:
				decky.logger.info("podman stopped successfully")
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
