from os import write
import paramiko
from yaml import safe_load
import getpass
from netmiko import ConnectHandler

user = input('Please provide your username:')
secret = getpass.getpass(prompt='Please provide your radius password:')

def basic_ssh_lab(host):
    ssh = ConnectHandler(device_type='cisco_nxos', ip=host, username=user, password=secret, conn_timeout=10,banner_timeout=200)
    global host_prompt
    host_prompt = ssh.find_prompt()
    print('connected to host ', host_prompt)
    ssh.enable()
    cli = 'show run snmp'
    output = ssh.send_command(cli)
    snmpv3_user = "cc-snmpcollector"
    if snmpv3_user in output:
        print('SNMPv3 user configured')
        snmpv3_verify = 'sh run | i cc-snmpcollector'
        snmpv3output = ssh.send_command(snmpv3_verify)
        print(snmpv3output)
        with open('snmpv3_log.txt', 'a') as log:
            log.write(host_prompt +'\n')
            log.write(snmpv3output + '\n')
    else:
        print('SNMPv3 user not configured')
        with open('snmpv3_missing.txt', "a") as log:
            log.write(host_prompt + '\n')

    ssh.disconnect()

with open("ipn_inventory.yaml", "r") as inv:
    host_root = safe_load(inv)
    host_count = int(len(host_root['region']))
    for x in range(0, host_count):
        try:
            for host in host_root['region'][x]['host']:
                print('CONNECTING TO HOST ' + host)
                basic_ssh_lab(host)
        except:
            print('Connection to host ' + host + ' failed')
            with open("failed_host.txt", "a") as failed:
                failed.write('Connection to host ' + host + ' failed\n')
                failed.close
quit()