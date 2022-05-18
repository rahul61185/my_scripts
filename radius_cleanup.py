from os import write
import paramiko
from yaml import safe_load
import getpass
from netmiko import ConnectHandler

user =  "i507802" #input('Please provide your username:')
secret = "SApH#c@6!!" #getpass.getpass(prompt='Please provide your radius password:')
inventory_file = input('please provide inventory file name:')

def basic_ssh_lab(hostname,ip):
    ssh = ConnectHandler(device_type='cisco_nxos', ip=ip, username=user, password=secret, conn_timeout=10,banner_timeout=200)
    global host_prompt
    host_prompt = ssh.find_prompt()
    if host_prompt:
        print('connected to host ', hostname)
        ssh.enable()
        # cli = ['show version', 'show run aaa'
        # ]
        cli = 'show run aaa'
        output = ssh.send_command(cli)
        # output = ssh.send_config_set(cli)
        print(output)
        if output:
            print('configuration completed for host ',host_prompt)
        ssh.disconnect()

with open(inventory_file, "r") as inv:
    host_root = safe_load(inv)
    host_list = []
    host_dict = host_root['all']['children']['device_roles_aci-ipn']['hosts']
    for key, val in host_dict.items():
        ip = val['ansible_host']
        hostname = key
        try:
            basic_ssh_lab(hostname,ip)
        except:
            print("couldn't find any host")

quit()