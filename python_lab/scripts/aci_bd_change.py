import requests
import getpass
from requests.api import head, post
import json
from requests import cookies
import urllib3
from urllib3.exceptions import HeaderParsingError
from urllib3 import disable_warnings, exceptions
from yaml import dump, safe_load
import time
from datetime import datetime
urllib3.disable_warnings()
import re

time= time.strftime("%Y%m%d_%H%M%S")

username = input("Please provide username only: ")
password = getpass.getpass(prompt='Please provide your radius password: ')
apic = input("Please provide IP Address of apic: ")
tenant_name = input('Please specify tennat name: ')
vrf_name = input('Please specify VRF Name: ')

def login_to_apic():
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
    if token:
        print("token generated \n")


def aci_bd_config():
    post_url= "https://" + apic + "/api/node/mo/uni/tn-"+ tenant_name +".json"
    payload = json.dumps({
        "fvBD": {
            "attributes": {
                "dn": "uni/tn-"+ tenant_name + "/BD-" + bd_name,
                "unicastRoute": "false",
                "status": "modified"
            }
        }
    })
    print('Posting following config to APIC...\n ')
    print(payload,'\n')
    headers = {'Cache-Control': "no-cache"}
    cookies = {
        'APIC-Cookie': token
        }
    
    response = requests.post(url=post_url, cookies=cookies,headers=headers, data=payload, timeout=15, verify=False)
    if response.status_code == 200:
        print('configuration completed:\n')

print('Start Time: ',time)

with open(r'inventory\aci_vrf_list.yaml', "r") as vrf:
    vrf_load = safe_load(vrf)
    tenant_len = len(vrf_load['tenant'])
    for x in range(0, tenant_len):
        if tenant_name == vrf_load['tenant'][x]['name']:
            vrf_len =  len(vrf_load['tenant'][x]['vrf'])
            for y in range(0, vrf_len):
                if vrf_name == vrf_load['tenant'][x]['vrf'][y]['name']:
                    for bd_name in vrf_load['tenant'][x]['vrf'][y]['interfaces']:
                        try:
                            login_to_apic()
                            aci_bd_config()
                        except:
                            print('Connection to host ' + apic + ' failed')
print('End Time :',time)
quit()
