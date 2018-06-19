#!/usr/bin/env python3
# 
# Author: Terry Jones, tjones@a10networks.com
# 
# Date:  JUN2018
#
# This script will login into the GLM server (glm.a10networks.com) using the user 
# credentials and perform one of the following actions:
#   * revoke the activation for a given ID(will release bandwidth from the vThunder back to the pool.
#   * revoke the license for a given ID
#   * activate a perpetual license
#
# Note: The information required for this script should be completed before this script is
# run. I would also recommend testing the script with the information completed to verify 
# functionality as well as ensure you are prepared for an emergency. 
#
# REVISIONS
#   0 - Initial generation
#

'''
Example configuration to register a vThunder with a Flexpool (subscription license)(ACOS v4.1.4-P1.69)

vThunder-Active-affinity-def-vMaster[4/1](config:2)#show run glm
!Section configuration: 94 bytes        
!
glm use-mgmt-port 
glm enable-requests 
glm allocate-bandwidth 200 
glm token vThd10516000
!
Run this command to update changes to GLM:

  glm send license-request

'''

__version__ = 0.1
__author__ = 'A10 Networks'

import json, argparse, requests

parser = argparse.ArgumentParser(description='This program will log into the GLM server and revoke the BW for a given vThunder.')
parser.add_argument('-p', '--password', default='a10', help='User password to access the GLM server (glm.a10networks.com)')
parser.add_argument('-u', '--username', default='admin', help='User email to access the GLM server (glm.a10networks.com)')
parser.add_argument('-d', '--uuid', default='3869D3001FD943DBA06B6A0E67F8B36D605C6360', help='show license uuid on vThunder')
parser.add_argument('-l', '--license_id', default='00000', help='where ID is locator found in url::https://glm.a10networks.com/licenses/ID/activations')
parser.add_argument('-i', '--id', default='00000', help='where ID must be located using API or website content search')
parser.add_argument('-a', '--account_id', default='000', help='where account_id is value found in url::https://glm.a10networks.com/licenses?account_id=XXX')

requests.packages.urllib3.disable_warnings()

try:
    args = parser.parse_args()
    password = args.password
    username = args.username
    id = args.id
    uuid = args.uuid
    account_id = args.account_id
    license_id = args.license_id

except Exception as e:
    print('ArgParser Error: ', e)


def glm_login():
    '''
    Description: Method to log into glm.a10networks.com and return the auth token for follow up api calls.
    '''
    requests.packages.urllib3.disable_warnings()

    json_header = {'Content-Type': 'application/json'}
    values = """
      {
        "user": {
          "email": "%s",
          "password": "%s"
        }
      }
    """ % (username, password)
    try:
        r = requests.post('https://glm.a10networks.com/users/sign_in.json', headers=json_header, data=values, verify=False)
        content = r.content
        parsed_json = json.loads(content)
        user_token = parsed_json['user_token']
        return user_token

    except Exception as e:
        print('Error in glm_login: ', e)


def get_entitlement_token(user_token):
    '''
    Description: Will return the entitlement token for a given license_id

    Requires: -l

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -l 13558
    '''
    requests.packages.urllib3.disable_warnings()
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }
    try:
        r = requests.get('https://glm.a10networks.com/licenses/'+license_id+'.json', headers=glm_headers, verify=False)
        content = r.content
        parsed_json = json.loads(content)
        ent_token = parsed_json['billing_serials']
        return ent_token[0][:-4]

    except Exception as e:
        print('Error in get_entitlement_token: ', e)


def get_uuid(user_token):
    '''
    Description: Returns all of the UUID(s) that are activated for a given license_id

    Requires: -l

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -p password -l 13558
    '''
    requests.packages.urllib3.disable_warnings()
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }
    try:
        r = requests.get('https://glm.a10networks.com/licenses/'+license_id+'/activations.json', headers=glm_headers, verify=False)
        content = r.content.decode()
        parsed_json = json.loads(content)
        uuid = []
        for i in parsed_json:
            uuid = uuid + [i['appliance_uuid']]
        return uuid

    except Exception as e:
        print('Error in get_uuid:', e)


def get_all_perpetual_licences(user_token):
    '''
    Description: Will return a list of id/Entitlement token pairs for all perpetual licenses

    Requires: -a

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -p password -a 411
    '''
    requests.packages.urllib3.disable_warnings()
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }
    try:
        r = requests.get('https://glm.a10networks.com/licenses.json?account_id='+account_id, headers=glm_headers,
                         verify=False)
        content = r.content.decode()
        parsed_json = json.loads(content)
        Entitlement_tokens = []
        for i in parsed_json:
           Entitlement_tokens = Entitlement_tokens + [i['id'], i['billing_serials']]
        return Entitlement_tokens

    except Exception as e:
        print('Error in get_all_licenses:', e)


def get_all_subscription_licences(user_token):
    '''
    Description: Will return a list of id/Entitlement token pairs for all subscription licenses

    Requires: -a

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -p password -a 411
    '''
    requests.packages.urllib3.disable_warnings()
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }
    try:
        r = requests.get('https://glm.a10networks.com/licenses.json?account_id='+account_id+'&tab=subscription', headers=glm_headers,
                         verify=False)
        content = r.content.decode()
        parsed_json = json.loads(content)
        Entitlement_tokens = []
        for i in parsed_json:
           Entitlement_tokens = Entitlement_tokens + [i['id'], i['billing_serials']]
        return Entitlement_tokens

    except Exception as e:
        print('Error in get_all_licenses:', e)


def activate_appliance(user_token):
    '''
    Description: Method will get the Entitlement token and will activate the appliance. The uuid must be included
    as argument to the script (else script will use the default, which will not be valid for your vThunder).

    Requires: -l, -d

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -p password -d D7C51F706CF9161F2907DB79AA9DFCADF7D239B7 -l 21225
    '''
    requests.packages.urllib3.disable_warnings()
    ent_token = get_entitlement_token(user_token)
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }
    values = """
      {
        "activation": {
          "appliance_uuid": "%s",
          "token": "%s",
          "version": "4.1 or newer"
        }
      }
    """ % (uuid, ent_token)
    flexpool_activations_url= 'https://glm.a10networks.com/activations.json'
    try:
        r = requests.post(flexpool_activations_url, headers=glm_headers,data=values, verify=False)
        content = r.content
        parsed_json = json.loads(content)
        for i in parsed_json:
            if i['appliance_uuid'] == uuid:
                key = i['key']
        return key

    except Exception as e:
        print('Error in activate_appliance:', e)


def revoke_license(user_token):
    '''
    Description: Revoke License

    Requires: -l

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -p password -l 19057
    '''
    requests.packages.urllib3.disable_warnings()
    glm_revoke_license_url = 'https://glm.a10networks.com/licenses/'+license_id+'.json'
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }
    try:
        r = requests.delete(glm_revoke_license_url, headers=glm_headers, verify=False)
        content = r.content
        return content.decode()

    except Exception as e:
        print('Error in revoke_license: ', e)


def revoke_activation(user_token):
    '''
    Description: Revoke Activation method will revoke the activation for a given id.

    Requires: -i, -l

    Example:
    python3 Flexpool_GLM_API_calls.py -u username@a10networks.com -p password  -i 23508 -l 19057

    '''

    requests.packages.urllib3.disable_warnings()
    glm_revoke_activation_url = 'https://glm.a10networks.com/activations/revoke.json'
    glm_activation_url = 'https://glm.a10networks.com/licenses/'+license_id+'/activations.json'
    glm_headers = {
        'Content-Type': 'application/json',
        'X-User-Email': username,
        'X-User-Token': user_token
    }

    try:
        r = requests.get(glm_activation_url,headers=glm_headers, verify=False)
        content = r.content.decode()
        parsed_json = json.loads(content)[0]
        lic_token = parsed_json['license_id']
        ids = parsed_json['id']
        values = """
              {
                "license-id": "%d",
                "ids": ["%d"
                ]
              }
            """ % (lic_token, ids)
        r = requests.patch(glm_revoke_activation_url, headers=glm_headers, data=values, verify=False)
        content = r.content.decode()
        parsed_json = json.loads(content)
        return r.status_code

    except Exception as e:
        print('Error in revoke_activation: ', e)


if __name__ == '__main__':

    glm_token=glm_login()
    #print('All perpetual entitlement tokens for '+username+': ',get_all_perpetual_licences(glm_token))
    #print('All subscription based entitlement tokens for '+username+': ',get_all_subscription_licences(glm_token))
    #print('The entitlement token for '+license_id+' is:', get_entitlement_token(glm_token))
    #print('uuid(s) for '+license_id+' are: ',get_uuid(glm_token))
    #print('Key for vThunder with uuid='+uuid+'\nkey::', activate_appliance(glm_token))
    #print(revoke_license(glm_token))
    #print('The vThunder associated with has been revoked. Status Code:', revoke_activation(glm_token))
