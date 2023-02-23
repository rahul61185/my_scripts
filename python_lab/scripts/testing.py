#Required libraries

from os import write
from yaml import safe_load
import getpass
from netmiko import ConnectHandler
import time
import threading

#User prompt variables

ios_hosts= input('\nPLEASE PROVIDE IP OF IOS HOST; IF THERE ARE MULTIPLE HOSTS, USE COMMA"(,)" to SEPERATE :')
nxos_hosts= input('\nPLEASE PROVIDE IP OF NXOS HOST; IF THERE ARE MULTIPLE HOSTS, USE COMMA"(,)" to SEPERATE :')
# target_host=input('\nPLEASE PROVIDE IP OF TARGET HOST; IF THERE ARE MULTIPLE HOSTS,\n'
#                 'THEN PLEASE USES A COMMA(,) TO SEPERATE THEM (Ex: 10.0.0.1,10.0.0.2,10.0.0.3):\n'
#                 'ELSE, SKIP IF YOU NEED TO RUN IT FOR ALL INVENTORY HOSTS: ')
inventory=input("If YOU NEED TO RUN THE SCRIPT FOR INVENTORY, THEN PLEAE PROVIDE INVENTORY's RELATIVE PATH : ")
print('!!!\n'
        'In next section, please provide IOS/NXOS commands or both if required;' '\n'
        'If only IOS command is supplied then script will run only for IOS devices;''\n'
        'If nxos command is supplied then script will run for nxos devices;''\n'
        'If both IOS and NXOS commands are supplied then script will run for both:\n'
        '!!!\n')
ios_cli= input('If TARGET IS AN IOS DEVICE, PROVIDE IOS COMMAND TO CHECK;\n'
                    'IF THERE ARE MULTIPLE COMMANDS, USE COMMA"(,)" to SEPERATE : ')
nxos_cli= input('If TARGET IS AN NXOS DEVICE, PROVIDE NXOS COMMAND TO CHECK;\n'
                    'IF THERE ARE MULTIPLE COMMANDS, USE COMMA"(,)" to SEPERATE : ')
user= input('Username: ')
tacacs_passwd = getpass.getpass(prompt='Password:')

time= time.strftime("%Y%m%d_%H%M%S")
log_file = 'log_file_'+time+'.csv'
missing_config= 'data_missing_'+time+'.csv'
failed='failed_host_'+time+'.csv'

#script Section

def ios_verification(host_ip):
    connection = ConnectHandler(
                device_type='cisco_ios',
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
        print('\n <<SUCCESS>>', host_promt)
    connection.enable()
    if ios_cli:
        ios_cli_var= ios_cli.split(',')
        cli_len=int(len(ios_cli_var))
        for i in range(0, cli_len):
            command=ios_cli_var[i]
            output = connection.send_command(command)
            connection.disconnect()
            if output:
                if 'Invalid' in output:
                    print('Invalid command, please verify the command!!')
                    with open(missing_config, "a") as logs:
                        logs.write(host_ip +' >> '+ host_promt+ ' \n' + output)
                        logs.close
                else:
                    # print('##Please refer below logs## \n')
                    print('OUTPUT FOR: ', command)
                    print(output+ '\n')
                    with open(log_file, "a") as logs:
                        logs.write(host_ip +' >> '+ host_promt+ '\n' + output + ' \n')
                        logs.close
            else:
                print('No matching data found for '+ command + '\n')
                with open(missing_config, "a") as missing:
                    missing.write(host_ip +' >> '+ host_promt + '\n No matching data found for '+ command + '\n')

def nxos_verification(host_ip):
    connection = ConnectHandler(
                device_type='cisco_ios',
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
        print('\n <<SUCCESS>>', host_promt)
    connection.enable()
    if nxos_cli:
        nxos_cli_var= nxos_cli.split(',')
        cli_len=int(len(nxos_cli_var))
        for i in range(0, cli_len):
            command=nxos_cli_var[i]
            output = connection.send_command(command)
            connection.disconnect()
            if output:
                if 'Invalid' in output:
                    print('Invalid command, please verify the command!!')
                    with open(missing_config, "a") as logs:
                        logs.write(host_ip +' ' + host_promt++ ',' + output + ' \n')
                        logs.close
                else:
                    # print('##Please refer below logs## \n')
                    print('OUTPUT FOR: ', command)
                    print(output+ '\n')
                    with open(log_file, "a") as logs:
                        logs.write(host_ip +' >> '+ host_promt+ '\n' + output + ' \n')
                        logs.close
            else:
                print('No matching data found for '+ command + '\n')
                with open(missing_config, "a") as missing:
                    missing.write(host_ip +' >> '+ host_promt + '\n No matching data found for '+ command + '\n')

#If a ios target host is supplied
if __name__ == "__main__":
    max_threads='10'
    threads = []
    # all_devices = [csr1000v1, csr1000v2, iosxrv9000, nxosv9000]
    # for device in all_devices:
    #     # Spawn threads and append to threads list
    #     th = threading.Thread(target=connect_and_fetch, args=(device,))
    #     threads.append(th)
    if ios_hosts:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
            'Checking IOS device in list...\n'
            '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
        host_var=ios_hosts.split(',')
        host_len=int(len(host_var))
        for x in range(0, host_len):
            host_ip=host_var[x]
            th = threading.Thread(target=ios_verification, args=(device,))
            threads.append(th)
            th.start()
            while True:
                alive_cnt = 0
                for t in self.threads:
                    if t.is_alive():
                        alive_cnt += 1
                if alive_cnt >=max_threads:
                    logging.info('Do not spawn new thread, already reached max limit of alive threads [%s]' % alive_cnt)
                    time.sleep(2)
                    continue
                break

    if nxos_hosts:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
            'Checking NXOS device in list...\n'
            '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

        host_var=nxos_hosts.split(',')
        host_len=int(len(host_var))
        for x in range(0, host_len):
            host_ip=host_var[x]
            th = threading.Thread(target=nxos_verification, args=(host_ip,))
            threads.append(th)
            th.start()
            while True:
                alive_cnt = 0
                for t in self.threads:
                    if t.is_alive():
                        alive_cnt += 1
                if alive_cnt >=max_threads:
                    logging.info('Do not spawn new thread, already reached max limit of alive threads [%s]' % alive_cnt)
                    time.sleep(2)
                    continue
                break
#If need to run for all inventory itmes
    if inventory:
        with open(inventory, "r") as inv:
            host_file = safe_load(inv)

        #For ios platform
            if ios_cli:
                for platform in host_file['platform']:
                    if platform['name']=='cisco_ios':
                        print('Checking CISCO_IOS Device in Inventory..')
                        item = platform['devices']
                        host_len=int(len(item))
                        for x in range(0, host_len):
                            host_ip=item[x]['ip']
                            name=item[x]['hostname']
                            if not host_ip:
                                print('!! NO NXOS Device found in inventory !!')
                            th = threading.Thread(target=nxos_verification, args=(host_ip,))
                            threads.append(th)
                            th.start()
                            while True:
                                alive_cnt = 0
                                for t in self.threads:
                                    if t.is_alive():
                                        alive_cnt += 1
                                if alive_cnt >=max_threads:
                                    logging.info('Do not spawn new thread, already reached max limit of alive threads [%s]' % alive_cnt)
                                    time.sleep(2)
                                    continue
                                break
            
        #For nxos platform
            if nxos_cli:
                for platform in host_file['platform']:
                    if platform['name']=='cisco_nxos':
                        print('Checking NXOS_IOS Device in Inventory..')
                        item = platform['devices']
                        host_len=int(len(item))
                        for x in range(0, host_len):
                            host_ip=item[x]['ip']
                            name=item[x]['hostname']
                            if not host_ip:
                                print('!! NO NXOS Device found in inventory !!')
                            th = threading.Thread(target=nxos_verification, args=(host_ip,))
                            threads.append(th)
                            th.start()
                            while True:
                                alive_cnt = 0
                                for t in self.threads:
                                    if t.is_alive():
                                        alive_cnt += 1
                                if alive_cnt >=max_threads:
                                    logging.info('Do not spawn new thread, already reached max limit of alive threads [%s]' % alive_cnt)
                                    time.sleep(2)
                                    continue
                                break    
    
    for thread in threads:
        thread.join()
quit()
