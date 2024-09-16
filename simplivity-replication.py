#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import requests
import datetime
import optparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import smtplib
from configobj import ConfigObj
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#### read config
config=ConfigObj("/starscripts/simplivity-check/config.cfg")
username=config['username']
password=config['password']
mailserver=config['mailserver']
rcpt=config['rcpt']
servers=config['hosts']
problem=0
alert=''

def connect_api():
	global alert,problem
	try:
		# Authenticate user and generate access token.
		response = requests.post(url+'oauth/token', auth=('simplivity', ''), verify=False, data={
		  'grant_type':'password',
		  'username':username,
		  'password':password})
		access_token = response.json()['access_token']

		# Add the access_token to the header.
		global headers
		headers = {'Authorization':  'Bearer ' + access_token, 'Accept' : 'application/vnd.simplivity.v1+json'}		

	except requests.exceptions.ConnectionError:
		print('Can not connect to Simplivity host '+server)
		alert+='Can not connect to Simplivity host '+server+'\n'
		problem=1
	except KeyError:
		print('Username or password is wrong for Simplivity host '+server)
		alert+='Username or password is wrong for Simplivity host '+server+'\n'
		problem=1


#--------------------------------------------------------------------

def get_host():
	global alert,problem,server
	try:
		global Host
		connect_api()
		try:
			response = requests.get(url+'hosts', verify=False, headers=headers)
			Hosts = dict()
			Hosts = response.json()['hosts']

			for Host in Hosts:
				if Host['management_ip'] == server:
					return Host
		except:
			Host= {
				"state": "Offline",
			}
			return Host

	except KeyError:
		print('Failed to get host state')
		alert='Failed to get Simplivity host state\n'
		problem=1

def get_replication_state():
	global alert,problem
	connect_api()
	get_host()

	response = requests.get(url+'virtual_machines', verify=False, headers=headers)
	VMs = dict()
	VMs = response.json()['virtual_machines']

	Errors=0
	Replication_error=''

	for VM in VMs:
		#print(VM['id'])
		#if VM['host_id'] == Host['id']: !!! disabled this because it was not queriyng all VMs
		response = requests.get(url+'virtual_machines/'+VM['id'], verify=False, headers=headers)
		VM_detail = dict()
		VM_detail = response.json()['virtual_machine']
		print(VM['name'] + ' has status ha: ' + VM_detail['ha_status'])
		#print VM_detail['ha_status']

		if VM_detail['ha_status'] != 'SAFE':
			Errors += 1
			if Errors >0:
				Replication_error += 'The storage HA status of ' + VM['name'] + ' is: ' + VM_detail['ha_status'] + '\n'

	if Errors == 0:
		return_msg = 'The storage HA status of all VMs is OK.'
	elif Errors > 0:
		alert += Replication_error
		problem=1
	else:
		alert+='Storage HA status unknown.'
		problem=1

#--------------------------------------------------------------------

def main():
	global url,server,rcpt,mailserver,alert,problem
	for server in servers:
		url = 'https://'+server+'/api/'
		get_replication_state()
		break # check only on one host
	print(problem)
	if problem == 1:
		alert+="\n\nScript CheckMK:/starscripts/simplivity-check/simplivity-replication-state.py"
		smtp=smtplib.SMTP(mailserver)
		smtp.sendmail(rcpt, rcpt, alert)
		print("ok")


# Start program
if __name__ == "__main__":
    main()

