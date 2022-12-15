import redis
import os, io
from minio import Minio
import traceback
import glob
import subprocess

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
print(redisClient)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

minioClient = Minio(minioHost, secure=False, access_key=minioUser, secret_key=minioPasswd)
print(minioClient)

bucket_name = "queue"
redis_queue = "toWorker"
output_bucket_name = "output2"

if not minioClient.bucket_exists(output_bucket_name):
    print(f"Create bucket {output_bucket_name}")
    minioClient.make_bucket(output_bucket_name)

while True:
    print("Inside while loop")
    try:
        print("Checking redis queue")
        work = redisClient.blpop(redis_queue, timeout=0)
        ##
        ## Work will be a tuple. work[0] is the name of the key from which the data is retrieved
        ## and work[1] will be the text log message. The message content is in raw bytes format
        ## e.g. b'foo' and the decoding it into UTF-* makes it print in a nice manner.
        ##
        song_hash = work[1].decode('utf-8')
        local_name = f"/data/input/{song_hash}.mp3"
        print(work[1].decode('utf-8'))

        print("get the song from minio")
        resp = minioClient.fget_object("queue", work[1].decode('utf-8'), local_name)

        print("Running demucs command")
        subprocess.run(["python3", "-m", "demucs.separate", "--mp3", "--out", "/data/output", local_name])

        print("uploading song")
        for mp3 in glob.glob(f"/data/output/mdx_extra_q/{song_hash}/*mp3"):
            track_name = mp3.split("/")[-1] # getting only the filename
            obj_name = f"{song_hash}/{track_name}"
            mp3_stream = io.BytesIO(open(mp3, "rb").read())

            minioClient.put_object(output_bucket_name, obj_name, mp3_stream, mp3_stream.getbuffer().nbytes)

    except Exception as exp:
        traceback.print_exc()
        print(f"Exception raised in log loop: {str(exp)}")
    # sys.stdout.flush()
    # sys.stderr.flush()