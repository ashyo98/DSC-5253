#!/usr/bin/env python3

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth

credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

#
# Stub code - just lists all instances
#
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


def wait_for_operation(compute, project, zone, operation):
    """
    Ref: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/compute/api/create_instance.py
    """
    print('Waiting for operation {} to finish...'.format(operation))
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)

def create_firewall_rule(name='allow-5000'):
    """
    Ref: https://cloud.google.com/compute/docs/reference/rest/v1/firewalls
    """

    firewall_body = {
        "name": name,
        "description": "allows TCP port 5000 to be accessed from anywhere (e.g. 0.0.0.0/0)",
        "sourceRanges": [
            "0.0.0.0/0"
        ],
        "targetTags": [
            name
        ],
        "allowed": [
            {
                "ports": ["5000"],
                "IPProtocol": ["tcp"]
            }
        ]
    }

    firewall_resp = service.firewalls().insert(project=project, body=firewall_body).execute()
    # print(firewall_resp)

def check_firewall_exists(name='allow-5000'):
    """
    Ref: https://cloud.google.com/compute/docs/reference/rest/v1/firewalls/list
    """
    response = service.firewalls().list(project=project).execute()

    for firewall in response['items']:
        if firewall['name'] == name:
            return True
    
    return False

def create_instance(name, zone='us-west1-a'):
    """
    Ref: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/compute/api/create_instance.py
         https://cloud.google.com/compute/docs/api/using-libraries#python
    """
    image_response = service.images().getFromFamily( project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
    source_disk_image = image_response['selfLink']
    machine_type = "zones/%s/machineTypes/f1-micro" % zone

    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup_script.sh'), 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [
                {
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    'key': 'startup-script',
                    'value': startup_script
                }
            ]
        }
    }

    tags_body = {
        "items": [
            "allow-5000"
        ],
        "fingerprint": ""
    }

    operation = service.instances().insert(project=project, zone=zone, body=config).execute()

    try:
        result = wait_for_operation(service, project, zone, operation['name'])
    except Exception as ex:
        print(ex)
        exit(1)

    # while service.zoneOperations().get(project=project, zone=zone, operation=operation['name']).execute()['status'] != 'DONE':
    #     time.sleep(3)
    
    # print("Instance Created")

    print("Your running instances are:")
    for instance in list_instances(service, project, zone):
        print(instance['name'])
    

    # print(instance)

    ip = instance["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
    
    tags_body["fingerprint"] = instance["tags"]["fingerprint"]
    
    response = service.instances().setTags(project=project, zone=zone, instance=name, body = tags_body).execute()

    # print(response)

    if not check_firewall_exists('allow-5000'):
        create_firewall_rule('allow-5000')

    print("Access the flask app here http://{}:5000".format(ip))


create_instance('lab5-part-1')

# for instance in list_instances(service, project, 'us-west1-b'):
#     pprint(instance)  