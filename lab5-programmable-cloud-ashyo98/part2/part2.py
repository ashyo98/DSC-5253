#!/usr/bin/env python3

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth

credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

base_instance_name = "lab5-part-1"

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

def create_snapshot(zone='us-west1-a'):
    """
    Ref: https://cloud.google.com/compute/docs/disks/create-snapshots#python
    """

    print("Creating a snapshot....")
    for instance in list_instances(service, project, zone):
        if instance["name"] == base_instance_name:
            disk_name = instance["disks"][0]["deviceName"]

    snapshot_body = {
        "name": "base-snapshot-{}".format(base_instance_name),
        "sourceDisk": disk_name
    }

    response = service.disks().createSnapshot(project=project, zone=zone, disk=base_instance_name, body=snapshot_body).execute()

    try:
        result = wait_for_operation(service, project, zone, response['name'])
    except Exception as ex:
        print(ex)
    
    print("snapshot {} successfully created".format("base-snapshot-{}".format(base_instance_name)))
    # pprint(result)

    # while service.zoneOperations().get(project=project, zone=zone, operation=response['name']).execute()['status'] != 'DONE':
    #         time.sleep(3)

    #delete command
    # gcloud compute snapshots delete base-snapshot-lab5-part-1

    return "base-snapshot-{}".format(base_instance_name)



def create_instance_from_snapshot(snapshot_name, instance_name, zone='us-west1-a'):
    """
    Ref: https://cloud.google.com/compute/docs/disks/restore-snapshot#python_2
    """
    machine_type = "zones/%s/machineTypes/f1-micro" % zone

    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup_script.sh'), 'r').read()

    config = {
        'name': instance_name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceSnapshot': "global/snapshots/{}".format(snapshot_name)
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

    response = service.instances().insert(project=project, zone=zone, body=config).execute()

    try:
        result = wait_for_operation(service, project, zone, response['name'])
    except Exception as ex:
        print(ex)
    
    tags_body = {
        "items": [
            "allow-5000"
        ],
        "fingerprint": ""
    }

    for instance in list_instances(service, project, zone):
        if instance['name'] == instance_name:
            break
    
    tags_body["fingerprint"] = instance["tags"]["fingerprint"]
    
    response = service.instances().setTags(project=project, zone=zone, instance=instance_name, body = tags_body).execute()

    ip = instance["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
    
    print("Successfully created a new instance: {}".format(instance_name))
    print("Access the instance here http://{}:5000".format(ip))
    
    # pprint(result)


# snapshot_name = create_snapshot()
snapshot_name = "snapshot-1"
base_name = "lab5-part-2"

print('Spawning new VMs from the snapshot....')
name_suffix = ['a', 'b', 'c']
for suffix in name_suffix:
    start_time = time.time()
    create_instance_from_snapshot(snapshot_name, base_name + suffix)
    print("--- %s seconds ---" % (time.time() - start_time))
