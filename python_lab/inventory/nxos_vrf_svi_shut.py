#Required libraries
from os import write
from yaml import safe_load
import getpass
from netmiko import ConnectHandler
import time
from datetime import datetime

time= time.strftime("%Y%m%d_%H%M%S")

vrf_source = input("PLEAE specificy if  DC or DMZ vrf list (Ex: dc, dmz):")
vrf = input('Please specify vrf name for which interfaces needs to be shut \n'
            'if there is more than one vrf then please use comma "," as seperator: ')
log_file = 'log_file_'+time+'.log'
action = input('please specify "shutdown" or "no shutdown": ')
target_ip = input('Please provide target Switch IP: ')
user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')
      

ssh_args = {
            "device_type": 'cisco_nxos',
            "host": '',
            "username": user,
            "password": tacacs_passwd,
            "secret": tacacs_passwd,
            "port": 22,
            "conn_timeout": 2,
            "banner_timeout": 200
            }

ssh_args_1=[]

if target_ip:
    host_var=target_ip.split(',')
    host_len=int(len(host_var))
    for x in range(0, host_len):

        host_ip=host_var[x]
        ssh_dummy = ssh_args.copy()
        ssh_dummy["host"] = host_ip
        ssh_args_1.append(ssh_dummy)

for item in ssh_args_1:

    try:

        with ConnectHandler(**item) as connection:

            global host_prompt
            print('\n Trying to connect host ', host_ip)
            host_promt=connection.find_prompt()
            if host_promt:
                print('\n <<SUCCESS>> Connected to host', host_promt)
            connection.enable()  
               
            with open(r'bsh_vrfs_list.yaml', "r") as v:
                vrf_load = safe_load(v)
                vrf_dict = vrf_load['vrf'][vrf_source]
                vrf_dict_len = len(vrf_dict)
                temp_vrf_list = []

            vrf_split = vrf.split(',')
            for item in vrf_split:
                temp_vrf_list.append(item)

            for temp_vrf in temp_vrf_list:
                for item in vrf_dict:
                    if item['vrf_name'] == temp_vrf:
                        for intf_name in item['interfaces']:
                            print(intf_name)
                            cli = ['interface ' + intf_name,
                                    action]

                            output = connection.send_config_set(cli)
                            print(output)

                            print("SUCCESS configuration completed ")
                            with open(log_file, "a") as logs:
                                logs.write(host_ip + ' \n' + output)
                                logs.close
            connection.disconnect
    except:
        print("ERROR!! Configuration Failed ")

quit()
