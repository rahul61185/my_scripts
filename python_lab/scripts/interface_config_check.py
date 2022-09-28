#Required libraries

from os import write
from yaml import safe_load
import getpass
from netmiko import ConnectHandler
import time

#User prompt variables

# inventory=input('Please provide inventory source absolute path: ')
# target_host=input('\nPLEASE PROVIDE IP OF TARGET HOST; IF THERE ARE MULTIPLE HOSTS, THEN PLEASE USES A COMMA(,)\n'
#                 'TO SEPERATE THEM (Ex: 10.0.0.1,10.0.0.2,10.0.0.3):\n'
#                 'ELSE, SKIP IF YOU NEED TO RUN IT FOR ALL INVENTORY HOSTS: ')
# print('!!!\n'
#         'In next section, please provide IOS/NXOS commands or both if required;' '\n'
#         'If only IOS command is supplied then script will run only for IOS devices;''\n'
#         'If nxos command is supplied then script will run for nxos devices;''\n'
#         'If both IOS and NXOS commands are supplied then script will run for all:\n'
#         '!!!\n')
# ios_command= input('If target is an IOS device, provide ios command to check else skip: ')
# nxos_command= input('If target is an NXOS device, provide nxos command to check else skip: ')
user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')
#
time= time.strftime("%Y%m%d_%H%M%S")
log_file = 'log_file_'+time+'.csv'
missing_device= 'missing_device_'+time+'.csv'
failed='failed_host_'+time+'.csv'

#script Section

def command_verification(host_ip,command,platform,intf_name):
    connection = ConnectHandler(
                device_type=platform,
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
    if host_promt:
        print('\n <<SUCCESS>> Connected to host', host_promt)
    connection.enable()
    output = connection.send_command(command)
    connection.disconnect()
    if output:
        if 'Invalid' in output:
            print('Invalid command, please verify the command!!')
            with open(missing_config, "a") as logs:
                logs.write(host_ip +' >> '+ host_promt+ ' \n' + output)
                logs.close
        else:
            print('##Please refer below logs## \n'+ command)
            print(output+ '\n')
            with open(log_file, "a") as logs:
                logs.write('\n'+ host_ip + ' >> '+host_promt+ ',' + intf_name +','+ output + '\n')
                logs.close
    else:
        print('No matching data found! \n')
        with open(missing_device, "a") as missing:
            missing.write(host_ip+','+ host_promt + command + '\n')


with open('inventory\mike_hosts.yaml', "r") as inv:
    mgmt_ip_src = safe_load(inv)
    for platform in mgmt_ip_src['platform']:
        if platform['name']=='cisco_ios':
            ios_hosts=platform['devices']
            len_ios = int(len(ios_hosts))
            # print(len_ios)
            for x in range(0, len_ios):
                temp_ip=ios_hosts[x]['ip']
                name=ios_hosts[x]['hostname']

                with open('inventory\mike_interfaces.yaml', "r") as intf:
                    intf_list =safe_load(intf)
                    # invt = intf_list['inventory']
                    # len = int(len(invt['hostname']))
                    for values in intf_list['inventory']:
                        host_name = (values['hostname'])
                        if host_name  == name:
                            for intf_var in values['interfaces']:
                                intf_name = intf_var
                                host_ip=temp_ip
                                platform='cisco_ios'
                                command= 'show run interface '+ intf_name + ' | i description'
                                try:
                                    command_verification(host_ip,command,platform,intf_name)
                                except:
                                    print('I caught an error for '+ host_ip + ' >> '+ host_name +' for  '+ command)
                                    with open(failed, "a") as fail:
                                        fail.write(host_name + command+'\n')
                                        fail.close


with open('inventory\mike_hosts.yaml', "r") as inv:
    mgmt_ip_src = safe_load(inv)
    for platform in mgmt_ip_src['platform']:
        if platform['name']=='cisco_nxos':
            nxos_hosts=platform['devices']
            len_nxos = int(len(nxos_hosts))
            # print(len_nxos)
            for x in range(0, len_nxos):
                temp_ip=nxos_hosts[x]['ip']
                name=nxos_hosts[x]['hostname']

                with open('inventory\mike_interfaces.yaml', "r") as intf:
                    intf_list =safe_load(intf)
                    # invt = intf_list['inventory']
                    # len = int(len(invt['hostname']))
                    for values in intf_list['inventory']:
                        host_name = (values['hostname'])
                        if host_name == name:
                            for intf_var in values['interfaces']:
                                intf_name = intf_var
                                host_ip=temp_ip
                                platform='cisco_nxos'
                                command= 'show run interface '+ intf_name + ' | i description'
                                try:
                                    print('\nCONNECTING TO HOST',x+1,'of',len_nxos,'; IP: ',host_ip)
                                    command_verification(host_ip,command,platform,intf_name)
                                except:
                                    print('I caught an error for '+ host_ip + ' >> '+ host_name +' for  '+ command)
                                    with open(failed, "a") as fail:
                                        fail.write(host_name + command+'\n')
                                        fail.close


quit()
