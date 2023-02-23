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
mac_file = 'addc_mac_table_'+time+'.csv'
unknown_mac_file = 'unknown_mac_file'+time+'.csv'

username = input("Please provide username only: ")
password = getpass.getpass(prompt='Please provide your radius password: ')
apic = input("Please provide IP Address of apic: ")
# api_query = input('Please provide API query  to fetch data: ') #'/api/node/class/fabricNode.json?order-by=fabricNode.id|asc' #

# mac_list= ['38-68-DD-01-CC-49',
#             "38-68-DD-01-CC-49",
#             "38-68-DD-01-C3-F1",
#             "38-68-DD-01-D4-49",
#             "38-68-DD-01-D4-48",
#             "00:23:e9:dc:40:02",
#             "00:23:e9:dc:40:03",
#             "00:23:e9:dc:40:04",
#             "00:23:e9:dc:40:05",
#             "00:23:e9:dc:40:02",
#             "00:23:e9:dc:40:03",
#             "00:23:e9:dc:40:04"
#             ]
with open(mac_file, "a") as logs:
    logs.write('mac_address,encap_vlan,leaf,interface')
    logs.close

with open(unknown_mac_file, "a") as logs:
    logs.write('mac_address')
    logs.close

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
        print("token generated")


# def aci_get_node():
#     print('##Collecting inventory##\n')
#     get_url = "https://"+ apic + "/api/node/class/fabricNode.json?order-by=fabricNode.id|asc"
#     cookies = {'APIC-Cookie': token}
#     response = requests.get(url=get_url, cookies=cookies, timeout=15, verify=False)
#     output = json.loads(response.text)
#     for items in output['imdata']:
#         node_id=items['fabricNode']['attributes']['name']
#         node_ip=items['fabricNode']['attributes']['address']
#         serial_number=items['fabricNode']['attributes']['serial']
#         model=items['fabricNode']['attributes']['model']
#         version=items['fabricNode']['attributes']['version']
#
#         with open(inv_file, "a") as logs:
#             logs.write('\n'+node_id +','+node_ip+','+model+','+serial_number+','+version)
#             logs.close

def aci_get_mac(mac):
    # print('##Collecting inventory##\n')
    get_url = 'https://' + apic + '/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.mac,'+'"'+ mac +'"'+')&rsp-subtree=full'
    cookies = {'APIC-Cookie': token}
    response = requests.get(url=get_url, cookies=cookies, timeout=15, verify=False)
    output = json.loads(response.text)

    if output['totalCount'] == '1':
        item = output
        raw_data=item['imdata']
        fvcep= item['imdata'][0]['fvCEp']
        vlan= fvcep['attributes']['encap'].replace('vlan-','')
        dn= fvcep['attributes']['dn'].split('/')
        tenant = dn[1].replace('tn-','')
        epg= dn[3].replace('epg-','')
        for path in output['imdata'][0]['fvCEp']['children']:
            if 'fvRsCEpToPathEp' in path:
                leaf_intf_1 = path['fvRsCEpToPathEp']['attributes']['tDn'].split('topology/pod-1/')
                leaf_intf_2 = leaf_intf_1[1].split('/pathep-')
                leaf_raw = leaf_intf_2[0]
                leaf = re.sub('\D+-', '', leaf_raw)
                intf_raw_1 = leaf_intf_2[1].replace('[','')
                intf=intf_raw_1.replace(']','')
                print(mac,vlan,leaf,intf)
                with open(mac_file, "a") as logs:
                    logs.write('\n'+mac+','+vlan+','+leaf+','+intf)
                    logs.close
    if output['totalCount'] == '0':
        print('MAC Address', mac, 'not active')
        with open(mac_file, "a") as logs:
            logs.write('\n'+mac+','+'no info found'+','+'no info found'+','+'no info found')
            logs.close



try:
    login_to_apic()
    with open('inventory\mac_address.yaml', "r") as mac:
        host_file = safe_load(mac)
        for mac in host_file['mac_address']:
            aci_get_mac(mac)


    # print('DATA COLLECTION COMPLETED')

except:
    print('Connection to host ' + apic + ' failed')

quit()
