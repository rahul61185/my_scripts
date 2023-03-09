#Required libraries
from os import write
from yaml import safe_load
import getpass
from netmiko import ConnectHandler
import time
from datetime import datetime

time= time.strftime("%Y%m%d_%H%M%S")

vrf_source = input("PLEAE specificy if  DC or DMZ vrf list (Ex: dc, dmz):")
user= 'admin' #input('Username: ')
tacacs_passwd = 'cisco123' #getpass.getpass(prompt='Password:')
vrf_name = input('Please specify vrf name for which interfaces needs to be shut: ')
target_ip = input('Please provide target Switch IP: ')
log_file = 'log_file_'+time+'.log'


def def_config_set(host_ip,intf_name):
    connection = ConnectHandler(
                device_type='cisco_nxos',
                host=host_ip,
                username=user,
                password=tacacs_passwd,
                secret=tacacs_passwd,
                port=22,
                conn_timeout=2,
                banner_timeout=200
                )
    global host_prompt
    print('\n Trying to connect host ', host_ip)
    host_promt=connection.find_prompt()    
    if host_promt:
        print('\n <<SUCCESS>> Connected to host', host_promt)
    connection.enable()
    cli = ['interface ' + intf_name,
            'shutdown']
   
    output = connection.send_config_set(cli)

    with open(log_file, "a") as logs:
        logs.write(host_ip + ' \n' + output)
        logs.close

    connection.disconnect

if target_ip:
    host_var=target_ip.split(',')
    host_len=int(len(host_var))
    for x in range(0, host_len):
        host_ip=host_var[x]

        with open(r'inventory\vrfs_list.yaml', "r") as vrf:
            vrf_load = safe_load(vrf)
            x_range = len(vrf_load['vrf'][vrf_source])
            
            for x in range(0, x_range):
                if vrf_name == vrf_load['vrf'][vrf_source][x]['name']:
                    for item in vrf_load['vrf'][vrf_source][x]['interfaces']:
                        intf_name = item
                        
                        try:
                            def_config_set(host_ip,intf_name)
                            print("SUCCESS configuration completed ")
                        except:
                            print("ERROR!! Configuration Failed ")
                
quit()