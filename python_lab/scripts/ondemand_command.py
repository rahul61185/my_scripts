#Required libraries

from os import write
from yaml import safe_load
import getpass
from netmiko import ConnectHandler
import time

#User prompt variables

ios_hosts= input('\nPLEASE PROVIDE IP OF IOS HOST; IF THERE ARE MULTIPLE HOSTS, USE COMMA"(,)" to SEPERATE :')
nxos_hosts= input('\nPLEASE PROVIDE IP OF NXOS HOST; IF THERE ARE MULTIPLE HOSTS, USE COMMA"(,)" to SEPERATE :')
# target_host=input('\nPLEASE PROVIDE IP OF TARGET HOST; IF THERE ARE MULTIPLE HOSTS,\n'
#                 'THEN PLEASE USES A COMMA(,) TO SEPERATE THEM (Ex: 10.0.0.1,10.0.0.2,10.0.0.3):\n'
#                 'ELSE, SKIP IF YOU NEED TO RUN IT FOR ALL INVENTORY HOSTS: ')
inventory=input("PLEAE PROVIDE INVENTORY's RELATIVE PATH : ")
print('!!!\n'
        'In next section, please provide IOS/NXOS commands or both if required;' '\n'
        'If only IOS command is supplied then script will run only for IOS devices;''\n'
        'If nxos command is supplied then script will run for nxos devices;''\n'
        'If both IOS and NXOS commands are supplied then script will run for both:\n'
        '!!!\n')
ios_command= input('If target is an IOS device, provide ios command to check else skip: ')
nxos_command= input('If target is an NXOS device, provide nxos command to check else skip: ')
user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')

time= time.strftime("%Y%m%d_%H%M%S")
log_file = 'log_file_'+time+'.csv'
missing_config= 'data_missing_'+time+'.csv'
failed='failed_host_'+time+'.csv'

#script Section

def command_verification(host_ip,command,os_type):
    connection = ConnectHandler(
                device_type=os_type,
                host=host_ip,
                username=user,
                password=tacacs_passwd,
                secret=tacacs_passwd,
                port=22,
                conn_timeout=10,
                banner_timeout=200
                )
    global host_prompt
    host_promt=connection.find_prompt()
    if host_promt:
        print('\n <<SUCCESS>> Connected to host', host_promt)
    connection.enable()
    output = connection.send_command(command)
    connection.disconnect()
    if output:
        if 'Invalid' in output:
            print('Invalid command, please verify the command!!')
            with open(missing_config, "a") as logs:
                logs.write(host_ip + ','+host_promt+ ',' + output + ' \n')
                logs.close
        else:
            print('##Please refer below logs## \n')
            print(output+ '\n')
            with open(log_file, "a") as logs:
                logs.write(host_ip + ','+host_promt+ ' \n' + output)
                logs.close
    else:
        print('No matching data found! \n')
        with open(missing_config, "a") as missing:
            missing.write(host_ip+','+ host_promt+ '\n')

#If a single target host is supplied

if ios_hosts:
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
          'Checking IOS device in list...\n'
          '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

    host_var=ios_hosts.split(',')
    host_len=int(len(host_var))
    for x in range(0, host_len):
        host_ip=host_var[x]
        if ios_command:
            command=ios_command
            os_type='cisco_ios'
        try:
            print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip,)
            command_verification(host_ip,command,os_type)
        except:
            print('Connection to ', host_ip,' failed')
            with open(failed, "a") as fail:
                fail.write(host_ip+'\n')
                fail.close

if nxos_hosts:
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
          'Checking NXOS device in list...\n'
          '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

    host_var=nxos_hosts.split(',')
    host_len=int(len(host_var))
    for x in range(0, host_len):
        host_ip=host_var[x]
        if nxos_command:
            command=nxos_command
            os_type='cisco_nxos'
        try:
            print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip,)
            print('\nConnecting to', host_ip)
            command_verification(host_ip,command,os_type)
        except:
            print('Connection to ', host_ip,' failed')
            with open(failed, "a") as fail:
                fail.write(host_ip+'\n')
                fail.close

#If need to run for all inventory itmes
if inventory:
    with open(inventory, "r") as inv:
        host_file = safe_load(inv)

    #For ios platform
        if ios_command:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
                  'Checking IOS device in inventory...\n'
                  '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

            for platform in host_file['platform']:
                if platform['name']=='cisco_ios':
                    os_type='cisco_ios'
                    item = platform['devices']
                    command=ios_command
                    host_len=int(len(item))
                    for x in range(0, host_len):
                        host_ip=item[x]['ip']
                        name=item[x]['hostname']
                        if not host_ip:
                            print('!! NO NXOS Device found in inventory !!')
                        try:
                            print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip,)
                            command_verification(host_ip,command,os_type)
                        except:
                            print('Connection to ', name,' failed')
                            if name:
                                with open(failed, "a") as fail:
                                    fail.write(host_ip +','+name+'\n')
                                    fail.close
                            else:
                                with open(failed, "a") as fail:
                                    fail.write(host_ip+'\n')
                                    fail.close

    #For nxos platform
        if nxos_command:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
                  'Checking NXOS device in inventory...\n'
                  '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

            for platform in host_file['platform']:
                if platform['name']=='cisco_nxos':
                    os_type='cisco_nxos'
                    item = platform['devices']
                    command=nxos_command
                    host_len=int(len(item))
                    for x in range(0, host_len):
                        host_ip=item[x]['ip']
                        name=item[x]['hostname']
                        if not host_ip:
                            print('!! NO NXOS Device found in inventory !!')
                        if not host_ip:
                            print('!! NO NXOS Device found in inventory !!')
                        try:
                            print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip,)
                            command_verification(host_ip,command,os_type)
                        except:
                            print('Connection to ', name,' failed')
                            if name:
                                with open(failed, "a") as fail:
                                    fail.write(host_ip +','+name+'\n')
                                    fail.close
                            else:
                                with open(failed, "a") as fail:
                                    fail.write(host_ip+'\n')
                                    fail.close

quit()
