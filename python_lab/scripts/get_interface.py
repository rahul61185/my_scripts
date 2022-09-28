#Required libraries
import threading
from os import write
from yaml import safe_load
import getpass
import time
from datetime import datetime
from napalm import get_network_driver
import json

#User prompt variables
inventory= input("PLEAE PROVIDE INVENTORY's RELATIVE PATH : ")

user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')

start_time= datetime.now()
time= time.strftime("%Y%m%d_%H%M%S")
down_intf = 'down_intf_list_'+time+'.csv'
all_intf = 'all_intf_list_'+time+'.csv'
failed='failed_host_'+time+'.csv'

#Defintion to gather facts
with open(all_intf, "a") as logs:
    logs.write('HOST,INTERFACE_NAME,STATUS,DESCRIPTION')
    logs.close

with open(down_intf, "a") as logs:
    logs.write('HOST,INTERFACE_NAME,STATUS,DESCRIPTION')
    logs.close

def find_interface(host_ip):
    driver = get_network_driver('ios')
    device = driver(host_ip, user, tacacs_passwd)
    device.open()
    raw_output = json.dumps(device.get_interfaces(), sort_keys=False)
    temp_json_load = list((json.loads(raw_output).items()))

    for key, val in temp_json_load:
        intf=str(key)
        intf_attr=str(val['is_up'])
        descr=str(val['description'])
        if intf_attr=='False':
            status='DOWN'
        else:
            status='UP'
        with open(all_intf, "a") as logs:
            logs.write('\n'+host_ip +','+ intf+','+status+','+descr)
            logs.close

        if intf_attr=='False':
            status='DOWN'
            with open(down_intf, "a") as logs:
                logs.write('\n'+host_ip +','+ intf+','+status+','+descr)
                logs.close

    device.close()

# calling inventory
if __name__ == "__main__":
    max_threads = 50
    threads = []

    if inventory:
        with open(inventory, "r") as inv:
            host_file = safe_load(inv)

            for platform in host_file['platform']:
                if platform['name']=='cisco_ios':
                    item = platform['devices']
                    host_len=int(len(item))
                    for x in range(0, host_len):
                        host_ip=item[x]['ip']
                        name=item[x]['hostname']
                        try:
                            print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip)
                            th = threading.Thread(target=find_interface(host_ip), args=(host_ip))
                            threads.append(th)
                            th.start()
                            print('<<SUCCESS>> DATA COLLECTION COMPLETED')
                            while True:
                                alive_cnt = 0
                                for t in threads:
                                    if t.is_alive():
                                        alive_cnt += 1
                                if alive_cnt >=max_threads:
                                    logging.info('Do not spawn new thread, already reached max limit of alive threads [%s]' % alive_cnt)
                                    time.sleep(2)
                                    continue
                                break
                        except:
                                    print("I caught an error for host", host_ip)
                                    with open(failed, "a") as logs:
                                        logs.write(host_ip)
                                        logs.close

    for thread in threads:
        thread.join()


    endtime= datetime.now()
    print('End time: ', endtime)

    quit()
