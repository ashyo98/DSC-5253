#!/bin/bash

mkdir -p /srv
cd /srv
curl http://metadata/computeMetadata/v1/instance/attributes/vm2_startup_script -H "Metadata-Flavor: Google" > vm2_startup_script.sh
curl http://metadata/computeMetadata/v1/instance/attributes/service_credentials -H "Metadata-Flavor: Google" > service-credentials.json
curl http://metadata/computeMetadata/v1/instance/attributes/vm1_launch_vm2_code -H "Metadata-Flavor: Google" > vm1_launch_vm2_code.py
export GOOGLE_CLOUD_PROJECT= $(curl http://metadata/computeMetadata/v1/instance/attributes/project -H "Metadata-Flavor: Google")

sudo apt-get update
sudo apt-get install -y python3 python3-pip git

pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 ./vm1_launch_vm2_code.py