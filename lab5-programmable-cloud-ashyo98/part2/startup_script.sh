#!/bin/bash

# build and install flask
export FLASK_APP=flaskr
flask init-db
nohup flask run -h 0.0.0.0 &