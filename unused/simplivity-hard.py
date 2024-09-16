#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import requests
import datetime
import optparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
######################################################################
# Parse Arguments
parser 		= optparse.OptionParser()
parser.add_option('-O', '--omnistack', help='IP of the OmniStack host', dest='arg_ominstack', type='string')
parser.add_option('-F', '--authfile', help='Json authfile user & password', dest='arg_authfile', type='string')
# parser.add_option('-U', '--username', help='OmniStack username (user@domain)', dest='arg_username', type='string')
# parser.add_option('-P', '--password', help='OmniStack password', dest='arg_password', type='string')

(opts, args) = parser.parse_args()

######################################################################
# Set the base URL for REST API requests.
global OVC_IP
OVC_IP = opts.arg_ominstack
url = 'https://'+OVC_IP+'/api/'

authfile=opts.arg_authfile
with open('./auth_simplivity.json') as json_data_file:
    data = json.load(json_data_file)
username=data['simplivity']['user']
password=data['simplivity']['passwd']

# Set Nagios data
return_code 	= { 'OK': 0, 'WARNING': 1, 'CRITICAL': 2, 'UNKNOWN': 3 }
return_msg 		= ''
return_perfdata = ''
hosts_excluded	= ''

######################################################################
# Functions

def connect_api():	
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
		print('Can not connect to host, please check IP address or hostname')
	except KeyError:
		print('Username or password error, please check and retry')

#--------------------------------------------------------------------	

def output_nagios(return_msg, return_perfdata, return_code):
	print(return_msg)
	sys.exit(return_code)

#--------------------------------------------------------------------

def get_host():
	try:
		
		global Host
		
		connect_api()
		response = requests.get(url+'hosts', verify=False, headers=headers)
		Hosts = dict()
		Hosts = response.json()['hosts']

		for Host in Hosts:
			if Host['management_ip'] == OVC_IP:
				return Host

	except KeyError:
		print('Failed to get host state')




def get_host_hardware_state():
	try:
		
		global return_msg
		
		connect_api()
		get_host()
		
		response = requests.get(url+'hosts/'+Host['id']+'/hardware', verify=False, headers=headers)
		
		Hardware = dict()
		Hardware = response.json()['host']
		
		if Hardware['status'] == 'GREEN':
			return_msg = 'The hardware status of ' + Host['name'] + ' is: ' + Hardware['status']
			output_nagios(return_msg,'',return_code['OK'])
		elif Hardware['status'] == 'YELLOW':
			return_msg = 'The hardware status of ' + Host['name'] + ' is: ' + Hardware['status']
			output_nagios(return_msg,'',return_code['WARNING'])
		elif Hardware['status'] == 'RED':
			return_msg = 'The hardware status of ' + Host['name'] + ' is: ' + Hardware['status']
			output_nagios(return_msg,'',return_code['CRITICAL'])
		else:
			return_msg = 'The hardware status of ' + Host['name'] + ' is: ' + Hardware['status']
			output_nagios(return_msg,'',return_code['UNKNOWN'])
		
	except KeyError:
		return_msg = 'Status unknown'
		output_nagios(return_msg,'',return_code['UNKNOWN'])

#--------------------------------------------------------------------

def main():

	get_host_hardware_state()

# Start program
if __name__ == "__main__":
    main()

