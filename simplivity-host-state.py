#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import requests
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import smtplib
import configparser
from configobj import ConfigObj
import pathlib
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#### read config
config=ConfigObj("/starscripts/simplivity-check/config.cfg")
username=config['username']
password=config['password']
mailserver=config['mailserver']
rcpt=config['rcpt']
servers=config['hosts']
smtp=smtplib.SMTP(mailserver)
problem=0
alert=''

######################################################################
# Functions
def connect_api():
	global alert
	global problem
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
	global alert
	global problem
	try:
		global Host
		global server
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

def get_host_state():
	global alert
	global problem
	try:
		global return_msg
		connect_api()
		get_host()
		if Host['state'] == 'ALIVE':
			return_msg = 'The node: ' + Host['name'] + ' is in state: ' + Host['state']
			print(return_msg)
		elif Host['state'] == 'FAILED':
			return_msg = 'The node: ' + Host['name'] + ' is in state: ' + Host['state']
			alert+=return_msg
			problem=1
		else:
			return_msg = 'The node: ' + Host['name'] + ' is in state: ' + Host['state']
			alert+=return_msg
			problem=1

	except KeyError:
		print('Failed to get Simplivity host state '+server)
		alert+='Failed to get Simplivity host state '+server+'\n'
		problem=1

#--------------------------------------------------------------------

def main():
	global url
	global server
	global rcpt,mailserver,alert
	for server in servers:
		url = 'https://'+server+'/api/'
		get_host_state()
	if problem == 1:
		alert+="\n\nScript CheckMK:/starscripts/simplivity-check/simplivity-host-state.py"
		smtp=smtplib.SMTP(mailserver)
		smtp.sendmail(rcpt, rcpt, alert)

# Start program
if __name__ == "__main__":
    main()

