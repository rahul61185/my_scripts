#python script to Add SNMP poll
import requests
import getpass
from requests.api import head, post
import json
from requests import cookies
import urllib3
from urllib3.exceptions import HeaderParsingError
from urllib3 import disable_warnings, exceptions
from yaml import dump, safe_load

urllib3.disable_warnings()


username = 'apic#Netsec_TACACS\\'+ input("Please provide username only:")
password = getpass.getpass(prompt='Please provide your radius password:')

def login_to_apic(apic):
    print('\n####Generating Token for '+ apic +' apic +:\n')
    login_url = "https://" + apic + "/api/aaaLogin.json"
    login_data = {
        "aaaUser": 
            {
                "attributes": {
                        "name": username,
                        "pwd": password 
                        }
                    }
                }
    headers = {
        "conetent-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    json_credentials = json.dumps(login_data)
    post_response = requests.post(url=login_url, data=json_credentials, headers=headers, timeout=15, verify=False)
    output = json.loads(post_response.text)
    auth_data = output["imdata"][0]["aaaLogin"]["attributes"]
    global token
    token = auth_data['token']
    version = auth_data['version']
    if '4.2(6l)' in version:
        print('Token generated, proceeding with further query:\n')
        print(apic ,'is running on ACI version is ', version)

# Snapshot creation task

# def snapshot(apic):
#     post_url= "https://" + apic + "/api/node/mo/uni/fabric/configexp-defaultOneTime.json"
#     payload = json.dumps({
#         "configExportP": {
#             "attributes": {
#                 "adminSt": "triggered",
#                 "descr": "mac_pinning_port_policy",
#                 "dn": "uni/fabric/configexp-defaultOneTime",
#                 "name": "defaultOneTime",
#                 "targetDn": "",
#                 "status": "created,modified",
#                 "snapshot": "true"
#             }
#         }
#     })
#     headers = {'Cache-Control': "no-cache"}
#     cookies = {
#         'APIC-Cookie': token
#         }
    
#     response = requests.post(url=post_url, cookies=cookies,headers=headers, data=payload, timeout=15, verify=False)
#     if response.status_code == 200:
#         print('snapshot created, proceeding with config change:\n')

# def mac_pinning(apic):
#     post_url= "https://" + apic + "/api/node/mo/uni/infra.json"
#     payload = json.dumps({
#         "lacpLagPol": {
#             "attributes": {
#                 "annotation": "",
#                 "ctrl": "fast-sel-hot-stdby,graceful-conv,susp-individual",
#                 "descr": "",
#                 "dn": "uni/infra/lacplagp-MAC_Pinning",
#                 "maxLinks": "16",
#                 "minLinks": "1",
#                 "mode": "mac-pin-nicload",
#                 "name": "MAC_Pinning",
#                 "nameAlias": "",
#                 "ownerKey": "",
#                 "ownerTag": ""
#             }
#         }
#     })
#     headers = {'Cache-Control': "no-cache"}
#     cookies = {
#         'APIC-Cookie': token
#         }
    
#     response = requests.post(url=post_url, cookies=cookies,headers=headers, data=payload, timeout=15, verify=False)
#     if response.status_code == 200:
#         print('configuration completed:\n')

# def mac_pinning_verify(apic):
#     post_url= "https://" + apic + "/api/node/mo/uni/infra/lacplagp-MAC_Pinning.json"
#     headers = {'Cache-Control': "no-cache"}
#     cookies = {
#         'APIC-Cookie': token
#         }
    
#     response = requests.get(url=post_url, cookies=cookies,headers=headers, timeout=15, verify=False)
#     output = json.loads(response.text)
#     if response.status_code == 200:
#         print(output)
#     else:
#         print('no config found')

# def snmp_config(apic,prefix):
#     print('##Configuring SNMP poller as per inventory##\n')
#     post_url = "https://" + apic + "/api/node/mo/uni/fabric/snmppol-default.json"
#     payload = json.dumps(
#         {
#             "snmpClientGrpP": {
#                 "attributes": {
#                     "dn": "uni/fabric/snmppol-default/clgrp-SNMP_exporter",
#                     "name": "SNMP_exporter",
#                     "descr": "SNMP_exporter",
#                     "rn": "clgrp-SNMP_exporter",
#                     "status": "created"
#                 },
#                 "children": [
#                     {
#                         "snmpClientP": {
#                             "attributes": {
#                                 "dn": 'uni/fabric/snmppol-default/clgrp-SNMP_exporter/client-['+ prefix +']',
#                                 "name": "SNMP_exporter",
#                                 "addr": prefix,
#                                 "rn": 'client-['+ prefix +']',
#                                 "status": "created"
#                             },
#                             "children": []
#                         }
#                     },
#                     {
#                         "snmpRsEpg": {
#                             "attributes": {
#                                 "tDn": "uni/tn-mgmt/mgmtp-default/oob-default",
#                                 "status": "created"
#                             },
#                             "children": []
#                         }
#                     }
#                 ]
#             }
#         }
#     )
#     headers = {'Cache-Control': "no-cache"}
#     cookies = {
#         'APIC-Cookie': token
#         }
    
#     response = requests.post(url=post_url, cookies=cookies,headers=headers, data=payload, timeout=15, verify=False)
#     if response.status_code == 200:
#         print('Configuration applied')

with open("apic_inventory.yaml", "r") as inv:
    host_root = safe_load(inv)
    region_count = int(len(host_root['region']))
    for x in range(0, region_count):
        for apic in host_root['region'][x]['host']:
            try:
                for prefix in host_root['region'][x]['prefix']:
                    print('CONNECTING TO HOST ' + apic)
                    login_to_apic(apic)
                    # snapshot(apic)
                    # mac_pinning_verify(apic)
            except:
                print('Connection to host ' + apic + ' failed')
                with open("failed_host.txt", "a") as failed:
                    failed.write('Connection to host ' + apic + ' failed\n')
                    failed.close
quit()
