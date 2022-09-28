#Required libraries
import threading
from os import write
from yaml import safe_load
import getpass
from netmiko import ConnectHandler
import time
from datetime import datetime
import concurrent.futures

#User prompt variables
inventory=input("PLEAE PROVIDE INVENTORY's RELATIVE PATH : ")

user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')

start_time= datetime.now()
time= time.strftime("%Y%m%d_%H%M%S")
log_file_acl = 'show_run_acl'+time+'.yaml'
log_file_acl_lines = 'show_run_acl'+time+'.yaml'
missing_config= 'data_missing_'+time+'.csv'
failed='failed_host_'+time+'.csv'

#script Section
print('Start time: ', start_time)
def find_acl_name(host_ip):
    connection = ConnectHandler(
                device_type='cisco_ios',
                host=host_ip,
                username=user,
                password=tacacs_passwd,
                secret=tacacs_passwd,
                port=22,
                conn_timeout=2,
                banner_timeout=200
                )
    global host_prompt
    host_promt=connection.find_prompt()

    print('\n Trying to connect host ', host_ip)
    if host_promt:
        print('\n <<SUCCESS>> Connected to host', host_promt)
    connection.enable()
    output = connection.send_command(command)
    connection.disconnect()
    if output:
        if 'invalid' in output:
            print('Command Error...Please verify the command')
        else:
            listfied_output = output.split('access')
            acl = listfied_output[1]

            with open(log_file_acl, "a") as logs:
                logs.write('\n- host_ip: '+ host_ip + '\n  acl_name: '+ acl)
                logs.close
    else:
        print('No matching data found! \n')
        with open(missing_config, "a") as missing:
            missing.write(host_ip, '\n')


if __name__ == "__main__":
    max_threads = 50
    threads = []

    if inventory:
        with open(inventory, "r") as inv:
            host_file = safe_load(inv)

            for platform in host_file['platform']:
                if platform['name']=='cisco_ios':
                    os_type='cisco_ios'
                    item = platform['devices']
                    command= 'show  running-config  | i snmp-server.*access'
                    host_len=int(len(item))
                    for x in range(0, host_len):
                        host_ip=item[x]['ip']
                        name=item[x]['hostname']
                        try:
                            print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip)
                            th = threading.Thread(target=find_acl_name(host_ip), args=(host_ip))
                            threads.append(th)
                            th.start()
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
                                logs.write(host_ip+'\n')
                                logs.close

    for thread in threads:
        thread.join()

endtime= datetime.now()
print('End time: ', endtime)

# quit()
