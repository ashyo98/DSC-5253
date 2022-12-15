#!/bin/bash

# setup flask installation
sudo apt-get update
sudo apt-get install -y python3 python3-pip git
git clone https://github.com/cu-csci-4253-datacenter/flask-tutorial
cd flask-tutorial
sudo python3 setup.py install
sudo pip3 install -e .

# build and install flask
export FLASK_APP=flaskr
flask init-db
nohup flask run -h 0.0.0.0 &

ip = `hostanme -I`

echo "Acccess the flask app here http://$ip:5000"