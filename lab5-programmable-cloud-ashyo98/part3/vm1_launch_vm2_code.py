#!/usr/bin/env python3

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth
import google.oauth2.service_account as service_account


# credentials, project = google.auth.default()
credentials = service_account.Credentials.from_service_account_file(filename='service-credentials.json')
project = os.getenv('GOOGLE_CLOUD_PROJECT') or 'csci-5253-dcsc-360905'
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

def create_instance(name, zone='us-west1-a'):
    image_response = service.images().getFromFamily( project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
    source_disk_image = image_response['selfLink']
    machine_type = "zones/%s/machineTypes/f1-micro" % zone

    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'vm2_startup_script.sh'), 'r').read()

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

    firewall_body = {
        "name": "allow-5000",
        "description": "allows TCP port 5000 to be accessed from anywhere (e.g. 0.0.0.0/0)",
        "sourceRanges": [
            "0.0.0.0/0"
        ],
        "targetTags": [
            "allow-5000"
        ],
        "allowed": [
            {
                "ports": ["5000"],
                "IPProtocol": ["tcp"]
            }

        ]
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

    for instance in list_instances(service, project, zone):
        if instance['name'] == name:
            print(instance['name'])
            break
    

    # print(instance)

    ip = instance["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
    
    tags_body["fingerprint"] = instance["tags"]["fingerprint"]
    
    response = service.instances().setTags(project=project, zone=zone, instance=name, body = tags_body).execute()

    # print(response)

    firewall_resp = service.firewalls().insert(project=project, body=firewall_body).execute() #TODO check if rule already exists
    # print(firewall_resp)

    print("Access the flask app here http://{}:5000".format(ip))


create_instance('lab5-part-3-vm2')

# for instance in list_instances(service, project, 'us-west1-b'):
#     pprint(instance)