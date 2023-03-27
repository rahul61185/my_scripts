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
log_file_acl_lines = 'show_acl_logs'+time+'.yaml'
missing_config= 'data_missing_'+time+'.csv'
failed='failed_host_'+time+'.csv'

#script Section
print('Start time: ', start_time)

def ios_config_acl(host_ip):
    connection = ConnectHandler(
                device_type= 'cisco_ios',
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
        print('\n <<SUCCESS>> Connected to host', host_ip)
    connection.enable()
    cli = ['ip access-list standard ' + acl_name,
            'permit 10.129.200.0 0.0.0.255',
            'do write']

    output = connection.send_config_set(cli)
    print(output)
    connection.disconnect()
    if output:
        if 'invalid' in output:
            print('Command Error...Please verify the command')
        else:
            print('Configuration completed')
    else:
        print('Configuration not pushed! \n')
        with open(missing_config, "a") as missing:
            missing.write(host_ip+','+ host_promt+ '\n')

def nxos_config_acl(host_ip):
    connection = ConnectHandler(
                device_type= 'cisco_ios',
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
        print('\n <<SUCCESS>> Connected to host', host_ip)
    connection.enable()
    cli = ['ip access-list  ' + acl_name,
            'permit ip 10.129.200.0 0.0.0.255 any',
            'copy run start']

    output = connection.send_config_set(cli)
    print(output)
    connection.disconnect()
    if output:
        if 'invalid' in output:
            print('Command Error...Please verify the command')
        else:
            print('Configuration completed')
    else:
        print('Configuration not pushed! \n')
        with open(missing_config, "a") as missing:
            missing.write(host_ip+','+ host_promt+ '\n')

if inventory:
    with open(inventory, "r") as inv:
        host_file = safe_load(inv)
        for platform in host_file['platform']:
            if platform['name'] ==  'cisco_ios':
                print('Connectiong to IOS hosts...')
                item = platform['devices']
                host_len = int(len(item))
                for x in range(0, host_len):
                    host_ip = item[x]['ip']
                    acl_name = item[x]['acl_mgmt']
                    try:
                        print('Trying to connect ios host ', x+1,' of ', host_len, 'ip: ', host_ip)
                        ios_config_acl(host_ip)
                    except:
                        print('Configuration not completed!!')

            if platform['name'] == 'cisco_nxos':
                print('Connectiong to NXOS hosts...')
                item = platform['devices']
                host_len = int(len(item))
                for x in range(0, host_len):
                    host_ip = item[x]['ip']
                    acl_name = item[x]['acl_mgmt']
                    try:
                        print('Trying to connect nxos host ', x+1,' of ', host_len, 'ip: ', host_ip)
                        nxos_config_acl(host_ip)
                    except:
                        print('Configuration not completed!!')



endtime= datetime.now()
print('End time: ', endtime)

# quit()
