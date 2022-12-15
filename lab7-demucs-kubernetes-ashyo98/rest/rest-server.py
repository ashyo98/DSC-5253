#!/usr/bin/python3
from flask import Flask, request, Response, send_file
import jsonpickle
import traceback
import base64
import redis
import os, io
import hashlib
from minio import Minio
import os,time,sys

flask_port = os.environ['FLASK_PORT']

app = Flask(__name__)

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

minioClient = Minio(minioHost, secure=False, access_key=minioUser, secret_key=minioPasswd)

bucket_name = "queue"
redis_queue = "toWorker"
output_bucket_name = "output"

if not minioClient.bucket_exists(bucket_name):
    print(f"Create bucket {bucket_name}")
    minioClient.make_bucket(bucket_name)

@app.route('/', methods=['GET'])
def hello():
    return '<h1> Music Separation Server</h1><p> Use a valid endpoint </p>'

@app.route('/hello', methods=['GET'])
def hello2():
    return '<h1> Hello</h1><p>endpoint is working</p>'

@app.route('/apiv1/separate', methods=['POST'])
def separate():
    try:
        request_payload = request.get_json()
        mp3_binary = request_payload["mp3"]
        hash_val = hashlib.sha1(mp3_binary.encode('utf-8')).hexdigest()

        # queue hash to redis
        redisClient.lpush(redis_queue, hash_val)

        # push the file to minio for the worker to take up separation
        mp3_stream = io.BytesIO(base64.b64decode(mp3_binary))
        minioClient.put_object(bucket_name, hash_val, mp3_stream, mp3_stream.getbuffer().nbytes)
        
        response = {'hash': hash_val, 'reason': 'song enqueued for separation'}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except Exception as ex:
        traceback.print_exc()
        response = {'reason': 'failed to enqueued song for separation. check logs for details.'}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=500, mimetype="application/json")

@app.route('/apiv1/queue', methods=['GET'])
def get_queue():
    try:
        queued_songs = redisClient.lrange(redis_queue, 0, -1)
        response = {'queue': [x.decode('utf-8') for x in queued_songs]}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    
    except Exception as ex:
        traceback.print_exc()
        response = {'reason': 'failed to fetch the queued songs in redis. check logs for details.'}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=500, mimetype="application/json")

@app.route('/apiv1/track/<songhash>/<track_name>', methods=['GET'])
def get_track(songhash, track_name):
    try:
        object_name = f"{songhash}/{track_name}.mp3"
        local_name = f"/tmp/{songhash}-{track_name}.mp3"
        resp = minioClient.get_object(output_bucket_name, object_name, local_name)
        resp_bytes = io.BytesIO(resp.data)
        return send_file(resp_bytes, as_attachment=True, download_name=f"{songhash}-{track_name}.mp3", mimetype='audio/mpeg')
    except Exception as ex:
        traceback.print_exc()
        response = {'reason': 'failed to fetch the song in minio. check logs for details.'}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=500, mimetype="application/json")
    finally:
        resp.close()
        resp.release_conn()

@app.route('/apiv1/remove/<songhash>/<track_name>', methods=['DELETE'])
def delete_track(songhash, track_name):
    try:
        object_name = f"{songhash}-{track_name}.mp3"
        minioClient.remove_object(output_bucket_name, object_name)
    except RecursionError as err:
        traceback.print_exc()
        response = {'reason': 'failed to remove the song in minio. check logs for details.'}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=500, mimetype="application/json")


app.run(host="0.0.0.0", port=flask_port)