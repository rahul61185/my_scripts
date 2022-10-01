#Required libraries
import threading
from os import write
from yaml import safe_load
import getpass
import time
from datetime import datetime
from napalm import get_network_driver
import json
import concurrent.futures

#User prompt variables
inventory= input("PLEAE PROVIDE INVENTORY's RELATIVE PATH : ")

user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')

start_time= datetime.now()
time= time.strftime("%Y%m%d_%H%M%S")
down_intf = 'down_intf_list_'+time+'.csv'
all_intf = 'all_intf_list_'+time+'.csv'
failed='failed_host_'+time+'.csv'
version_file= 'os_version_'+time+'.csv'
#Defintion to gather facts
with open(version_file, "a") as logs:
    logs.write('HOST,IOS/NXOS,VERSION')
    logs.close

print('Start time: ',start_time)

def find_interface(host_ip):
    driver = get_network_driver(os_type)
    connection={"hostname": host_ip,
                "username": user,
                "password": tacacs_passwd,
                "optional_args":
                    {
                        "secret": tacacs_passwd
                        }
                    }
    # device = driver(connection)
    with driver(**connection) as device:
        device.open()
        raw_output = device.get_facts()
        if raw_output:
            print("CONNECTED TO HOST ",name)
        # version=raw_output["os_version"]
        version=raw_output["os_version"]
        with open(version_file, "a") as logs:
            logs.write('\n'+host_ip +','+type+ ','+ version)
            logs.close
        device.close()


if inventory:
    with open(inventory, "r") as inv:
        host_file = safe_load(inv)

        for platform in host_file['platform']:
            type='IOS'
            if platform['name']=='cisco_ios':
                print('\n LOOKING FOR IOS DEVICES...')
                os_type='ios'
                item = platform['devices']
                host_len=int(len(item))
                for x in range(0, host_len):
                    host_ip=item[x]['ip']
                    name=item[x]['hostname']
                    try:
                        print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip)
                        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                            executor.map(find_interface(host_ip), host_ip)
                            print('<<SUCCESS>> DATA COLLECTION COMPLETED')

                    except:
                        print("I caught an error for host", host_ip)
                        with open(failed, "a") as logs:
                            logs.write(host_ip+ '\n')
                            logs.close

            if platform['name']=='cisco_nxos':
                type='NXOS'
                print('\n LOOKING FOR NXOS DEVICES...')
                os_type='nxos_ssh'
                item = platform['devices']
                host_len=int(len(item))
                for x in range(0, host_len):
                    host_ip=item[x]['ip']
                    name=item[x]['hostname']
                    try:
                        print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip)
                        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                            executor.map(find_interface(host_ip), host_ip)
                            print('<<SUCCESS>> DATA COLLECTION COMPLETED')

                    except:
                        print("I caught an error for host", host_ip)
                        with open(failed, "a") as logs:
                            logs.write(host_ip+ '\n')
                            logs.close

    endtime= datetime.now()
    print('End time: ', endtime)

quit()
