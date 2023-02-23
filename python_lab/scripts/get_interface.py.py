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
intf_count= 'intf_count_'+time+'.csv'
#Defintion to gather facts
with open(all_intf, "a") as logs:
    logs.write('HOST,INTERFACE_NAME,STATUS,DESCRIPTION')
    logs.close

with open(down_intf, "a") as logs:
    logs.write('HOST,INTERFACE_NAME,STATUS,DESCRIPTION')
    logs.close

with open(intf_count, "a") as logs:
    logs.write('HOST,UP,DOWN')
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
        raw_output = json.dumps(device.get_interfaces(), sort_keys=False)
        if raw_output:
            print("CONNECTED TO ", host_ip)
        temp_json_load = list((json.loads(raw_output).items()))

        down_intf_list=[]
        up_intf_list=[]

        for key, val in temp_json_load:
            if ('Vlan' not in key) and ('nnel' not in key) and('anagement' not in key) and('mgmt' not in key) and('oopback' not in key):
                intf=str(key)
                intf_attr=str(val['is_up'])
                descr=str(val['description'])
                if intf_attr=='False':
                    status='DOWN'
                else:
                    status='UP'
                    up_intf_list.append(status)

                with open(all_intf, "a") as logs:
                    logs.write('\n'+host_ip +','+ intf+','+status+','+descr)
                    logs.close

        down_count = str(down_intf_list.count('DOWN'))
        up_count = str(up_intf_list.count('UP'))

    with open(intf_count, "a") as logs:
        logs.write('\n'+host_ip +','+ up_count+','+down_count)
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