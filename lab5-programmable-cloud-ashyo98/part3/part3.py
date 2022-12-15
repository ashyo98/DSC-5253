#!/usr/bin/env python3

import argparse
import os
import time
import traceback
from pprint import pprint

import googleapiclient.discovery
import google.auth
import google.oauth2.service_account as service_account

#
# Use Google Service Account - See https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html#module-google.oauth2.service_account
#
credentials = service_account.Credentials.from_service_account_file(
    filename='service-credentials.json')
project = os.getenv('GOOGLE_CLOUD_PROJECT') or 'csci-5253-dcsc-360905'
# credentials, project = google.auth.default()
service = googleapiclient.discovery.build(
    'compute', 'v1', credentials=credentials)

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
    image_response = service.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
    source_disk_image = image_response['selfLink']
    machine_type = "zones/%s/machineTypes/f1-micro" % zone

    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'vm1_startup_script.sh'), 'r').read()

    vm2_startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'vm2_startup_script.sh'), 'r').read()

    vm1_launch_vm2_code = open(
        os.path.join(
            os.path.dirname(__file__), 'vm1_launch_vm2_code.py'), 'r').read()

    service_credentials = open(
        os.path.join(
            os.path.dirname(__file__), 'service-credentials.json'), 'r').read()

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
                    # Ref: https://cloud.google.com/compute/docs/instances/startup-scripts/linux
                    'key': 'startup-script',
                    'value': startup_script
                },
                {
                    'key': 'vm2_startup_script',
                    'value': vm2_startup_script
                },
                {
                    'key': 'vm1_launch_vm2_code',
                    'value': vm1_launch_vm2_code
                },
                {
                    'key': 'service_credentials',
                    'value': service_credentials
                }
            ]
        }
    }

    service_account_req_body = {
        "email": "lab5-662@csci-5253-dcsc-360905.iam.gserviceaccount.com",
        "scopes": [
            "https://www.googleapis.com/auth/compute"
        ]
    }

    operation = service.instances().insert(project=project, zone=zone, body=config).execute()

    try:
        result = wait_for_operation(service, project, zone, operation['name'])
    except Exception as ex:
        print(traceback.format_exc())
        exit(1)

    
    print("VM instance {} created successfully.".format(name))

    # print("Your running instances are:")
    # for instance in list_instances(service, project, zone):
    #     if instance is not None:
    #         print(instance['name'])

    # Ref: https://cloud.google.com/compute/docs/reference/rest/v1/instances/setServiceAccount#authorization-scopes

    # request = service.instances().setServiceAccount(project=project, zone=zone, instance=name, body=service_account_req_body).execute()

    # try:
    #     result = wait_for_operation(service, project, zone, request['name'])
    # except Exception as ex:
    #     print(traceback.format_exc())
    #     exit(1)

    # pprint(result)


create_instance('lab5-part-3-vm1')
