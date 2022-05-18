from os import write
import paramiko
from yaml import safe_load
import getpass
from netmiko import ConnectHandler

user = input('Please provide your username:')
secret = getpass.getpass(prompt='Please provide your radius password:')

def add_acl_vty(host):
    ssh = ConnectHandler(device_type='cisco_nxos', ip=host, username=user, password=secret, conn_timeout=10,banner_timeout=200)
    global host_prompt
    host_prompt = ssh.find_prompt()
    print('connected to host ', host_prompt)
    ssh.enable()
    acl_line = '147.204.224.0/22'
    cli = ['ip access-list ACL_SNMP_VTY',
    '5 permit ip 147.204.224.0/22 any',
    'resequence ip access-list ACL_SNMP_VTY 10 10',
    'copy run start'
    ]
    output = ssh.send_config_set(cli)
    print(output)
    if output:
        print('configuration completed for host ',host_prompt)
    ssh.disconnect()

with open("ipn_inventory.yaml", "r") as inv:
    host_root = safe_load(inv)
    region_count = int(len(host_root['region']))
    for x in range(0, region_count):
        for host in host_root['region'][x]['host']:
            try:
                print('CONNECTING TO HOST ' + host)
                add_acl_vty(host)
            except:
                print('Connection to host ' + host + ' failed')
                with open("failed_host.txt", "a") as failed:
                    failed.write('Connection to host ' + host + ' failed\n')
                    failed.close
quit()