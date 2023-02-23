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
def def_config_set(host_ip):
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
        print('\n <<SUCCESS>> Connected to host', host_ip)
    connection.enable()
    cli = ['ip access-list extended ALLOW_NTP',
            '10 permit udp host 10.224.0.1 eq ntp any',
            '20 permit udp host 10.190.0.1 eq ntp any',
            '30 permit udp any host 10.224.0.1 eq ntp',
            '40 permit udp any host 10.190.0.1 eq ntp',
            '50 deny ip any any',
            'exit',
            'clock  timezone UAE 4 0',
            'ntp authentication-key 1 md5 3nbd!$ync',
            'ntp authenticate',
            'ntp trusted-key 1',
            'ntp source ' + source_int ,
            'ntp server 10.224.0.1 key 1',
            'ntp server 10.190.0.1 key 1 prefer',
            'ntp access-group peer ALLOW_NTP',
            'do write'
            ]

    # cli = [acl, resequence, snmp_host, 'copy run start', verify]
    output = connection.send_config_set(cli)
    # ConnectHandler.config(cli)

    if output:
        if 'invalid' in output:
            print('Command Error...Please verify the command')
        else:
            print('Configuration completed')
    else:
        print('Configuration not pushed! \n')
        with open(missing_config, "a") as missing:
            missing.write(host_ip+','+ host_promt+ '\n')

    connection.disconnect()

if __name__ == "__main__":
    max_threads = 50
    threads = []

    if inventory:
        with open(inventory, "r") as inv:
            host_file = safe_load(inv)
            host_len=int(len(host_file))
            for x in range(0, host_len):
                host_ip=host_file[x]['host_ip']
                source_int = str(host_file[x]['mgmt_interface'])
                try:
                    print('\nCONNECTING TO HOST',x+1,'of',host_len,'; IP: ',host_ip)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                        executor.map(def_config_set(host_ip), host_ip)
                except:
                    print("I caught an error for host", host_ip)
                    with open(failed, "a") as logs:
                        logs.write(host_ip +  '\n')
                        logs.close

    # for thread in threads:
    #     thread.join()

endtime= datetime.now()
print('End time: ', endtime)

# quit()
