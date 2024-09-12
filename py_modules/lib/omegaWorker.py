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
import time 
import io
import configparser
from subprocess import Popen, PIPE, CalledProcessError
from getpass import getpass

class WorkerClass:
	def SelfCreateProtocol(self,lip):
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

	def createIpVlanC(self,sdsubn,sdgway):
		podnet = f"podman network create --subnet={sdsubn} --gateway={sdgway} --driver=ipvlan -o parent=wlan0 xivlanc"
		try:
			xivnet = subprocess.run(shlex.split(podnet),check=True,capture_output=True)
			if xivnet.returncode == 0:
				decky.logger.info("podman ipvlan network xivlanc has been created")
		except subprocess.CalledProcessError as e: 
			decky.logger.info(e.stderr.decode())
	
	def fixPodmanStorage(self):
		podstorecmd = "cp /home/deck/xivomega/storage/storage.conf /etc/containers/storage.conf"
		psf = subprocess.run(shlex.split(podstorecmd),check=True,capture_output=True)
		try:
		   	if psf.returncode==0:
		   		decky.logger.info("/etc/containers/storage.conf was patched")
		   		pass
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())

	def SetRoutes(self,rt14):
		for r in rt14:
			way = f"ip route add {r} via 10.88.0.7"
			nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
			try:
		   		if nav.returncode==0:
		   			decky.logger.info(f"route to {r} added")
			except subprocess.CalledProcessError as e:
				decky.logger.info(e.stderr.decode())

	def ClearNetavarkRules(self):
		subprocess.run(shlex.split("iptables -F INPUT"),check=True,capture_output=True)
		subprocess.run(shlex.split("iptables -F FORWARD"),check=True,capture_output=True)
		subprocess.run(shlex.split("iptables -F OUTPUT"),check=True,capture_output=True)

	def PrintLogo(self):
		subprocess.call(pth + "titleCard.sh")

	def ReconnectProtocol(self):
		subprocess.run(shlex.split("podman restart xivomega"),check=True,capture_output=True)
		subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
		subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)

	def CDTimer(self):
		for i in range(10, 0, -1):
			decky.logger.info(i, end = ' \r')
			time.sleep(1)

	def CreateHostAdapter(self,virtual_ip,netbits,broadcast):
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

	def SelfDestructProtocol(self):
		decky.logger.info("Terminating Mitigation Protocol and XIVOmega")
		for r in roadsto14:
			way = f"ip route del {r} via 10.88.0.7"
			nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
			try:
		   		if nav.returncode==0:
		   			decky.logger.info(f"route to {r} deleted")
			except subprocess.CalledProcessError as e:
					decky.logger.info(e.stderr.decode())
		try:
			panto = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if panto.returncode == 0:
				decky.logger.info("XIVOmega Container Stopped")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		try:
			atomic = subprocess.run(shlex.split("podman network disconnect xivlanc xivomega"),check=True,capture_output=True)
			if atomic.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Disconnected")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				decky.logger.info("XIVOmega IPVlan Removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				decky.logger.info("XIVOmega Container removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				decky.logger.info("Host IPVlan turned off")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				decky.logger.info("Host IPVlan removed")
		except subprocess.CalledProcessError as e:
			decky.logger.info(e.stderr.decode())
		decky.logger.info("All done - Goodbye")

	def SelfCleaningProtocol(self):
		ccnt = 0
		for r in roadsto14:
			way = f"ip route del {r} via 10.88.0.7"
			try:
				nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
				if nav.returncode==0:
		   			ccnt = ccnt + 1
		   			decky.logger.info(f"route to {r} deleted")
			except subprocess.CalledProcessError as e:
				decky.logger.info(e.stderr.decode())
				pass
		try:
			bworld = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				ccnt = ccnt +1
		except subprocess.CalledProcessError as e:
			pass
		if (ccnt > 0):
			decky.logger.info("Dangling elements from previous play session detected. CleanUp Protocol Activated and Completed")
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
				decky.logger.info("podman stopped successfully")
		except subprocess.CalledProcessError as e:
			pass
			decky.logger.info(e.stderr.decode())

class RootRequiredError(RuntimeError):
	pass

class InvalidIPException(Exception):
	pass

class ConnectionFailedError(Exception):
	pass

class NonExistentException(Exception):
	pass
