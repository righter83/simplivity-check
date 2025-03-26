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
rcptboe =
rcptram =
splitrcpt
hosts =
``` 
In Hosts you can define multiple Servers with like 1.1.1, 2.2.2.2

Then you have to configure the config file in both scripts on line 16 (Full Path):
``` 
config=ConfigObj("/xxx/config.cfg")
``` 

## v1.1 Split Recipient Function
Now there is an option for Multiple Recipient, if you have multiple Admins for different Clusters.
You can then set splitrcpt = 1 in the config and then use rcptboe and rcptram.
!!! Then you have to change the hardcoded if cause in both scripts to regex the Simplivity Host IP or the Cluster Name

# How to use
Just call the scripts
``` 
./simplivity-host-state.py
./simplivity-replication.py
``` 

