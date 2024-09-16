# Info
This scripts has been forked. 
Initially it was desgined for Nagios. I rewrote it to run via crontab and Errors are beeing reported over Mail.
It uses a config file.
I updated it to be able to run with Pyhton 3 and added some error handling


# Configuration

## Read User
For the Simplivity API Access you have to create a read only user in vCenter first.

## Config File
Create a config file in that folder with name config.cfg
```
username = 
password = 
mailserver = 
rcpt = 
hosts =
``` 
In Hosts you can define multiple Servers with like 1.1.1, 2.2.2.2

Then you have to configure the config file in both scripts on line 16 (Full Path):
``` 
config=ConfigObj("/xxx/config.cfg")
``` 

# How to use
Just call the scripts
``` 
./simplivity-host-state.py
./simplivity-replication-state.py
``` 

