from __future__ import print_function
import logging
import random
import time
import sys
import base64
import grpc
import lab6_grpc_pb2
import lab6_grpc_pb2_grpc

def doAdd(stub, debug=False):
    response = stub.PerformAdd(lab6_grpc_pb2.addMsg(a=5, b=10))
    if debug:
        print("client received: {}".format(response.sum))

def doRawImage(stub, debug=False):
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    response = stub.ImageDimensions(lab6_grpc_pb2.rawImageMsg(img=img))
    if debug:
        print("client received width:{} height:{} ".format(response.width, response.height))

def doDotProduct(stub, debug=False):
    list_size = 100

    a, b = [], [] 
    for _ in range(list_size):
        a.append(random.random())
    for _ in range(list_size):
        b.append(random.random())
    
    response = stub.PerformDotProduct(lab6_grpc_pb2.dotProductMsg(a=a, b=b))
    if debug:
         print("client received dotProduct:{} ".format(response.dotproduct))

def doJsonImage(stub, debug=False):
    with open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb') as img:
        encoded_string = base64.b64encode(img.read()).decode()
    response = stub.JsonImageDimensions(lab6_grpc_pb2.jsonImageMsg(img=encoded_string))
    
    if debug:
        print("client received width:{} height:{} ".format(response.width, response.height))
    

if __name__ == '__main__':
    logging.basicConfig()
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <server ip> <cmd> <reps>")
        print(f"where <cmd> is one of add, rawImage, sum or jsonImage")
        print(f"and <reps> is the integer number of repititions for measurement")

    host = sys.argv[1]
    cmd = sys.argv[2]
    reps = int(sys.argv[3])

    addr = f"{host}:50051"
    print(f"Running {reps} reps against {addr}")

    with grpc.insecure_channel(str(addr)) as channel:
        stub = lab6_grpc_pb2_grpc.Lab6GrpcStub(channel)

        if cmd == 'rawImage':
            start = time.perf_counter()
            for x in range(reps):
                doRawImage(stub)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        elif cmd == 'add':
            start = time.perf_counter()
            for x in range(reps):
                doAdd(stub, debug=False)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        elif cmd == 'jsonImage':
            start = time.perf_counter()
            for x in range(reps):
                doJsonImage(stub, debug=False)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        elif cmd == 'dotProduct':
            start = time.perf_counter()
            for x in range(reps):
                doDotProduct(stub, debug=False)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        else:
            print("Unknown option", cmd)