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
date=time.strftime("%Y%m%d")
# time= time.strftime("%Y%m%d_%H%M%S")
# down_intf = 'down_intf_list_'+time+'.csv'
inv_file = 'cisco_inventory_'+date+'.csv'
failed='failed_host_'+date+'.csv'
# intf_count= 'intf_count_'+time+'.csv'
#Defintion to gather facts
with open(inv_file, "a") as logs:
    logs.write('HOST,IP,Model,SERIAL_NUMBER, OS_VERSION')
    logs.close

print('Start time: ',start_time)

def find_interface(host_ip):
    driver = get_network_driver(ios_type)
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
        raw_output=json.dumps(device.get_facts())
        data=json.loads(raw_output)
        hostname=data['hostname']
        serial=data['serial_number']
        ip= host_ip
        model= data['model']
        os_version=data['os_version']

        with open(inv_file, "a") as logs:
            logs.write('\n'+hostname +','+ host_ip+','+model+','+serial+',"'+os_version+'"')
            logs.close

        device.close()

if inventory:
    with open(inventory, "r") as inv:
        host_file = safe_load(inv)

        for platform in host_file['platform']:
            if platform['name']=='cisco_ios':
                print('Looking for IOS Devices...')
                item = platform['devices']
                ios_type= 'ios'
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
                print('Looking for NXOS Devices...')
                item = platform['devices']
                ios_type='nxos_ssh'
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
