# Timing Table


|  Method 	        |   Local  | Same-Zone | Different Region |
|-------------------|--------  |-----------|------------------|	 	
|   REST add	    |  2.45 ms |   2.52 ms 	     |     286.8 ms            |
|   gRPC add	    |  0.47 ms |   0.51 ms 	     |     144.34 ms            |
|   REST rawimg	    |  4.25 ms |   6.30 ms 	     |    1178.56 ms	            |
|   gRPC rawimg	    |  7.90 ms |   8.35 ms 	     |     194.5 ms            | 
|   REST dotproduct	|  2.80 ms |   2.90 ms 	     |     287.72 ms            |
|   gRPC dotproduct	|  0.67 ms |   0.70 ms 	     |     143.95 ms	            |
|   REST jsonimg	| 31.63 ms |  37.44 ms    |    1321.95 ms    |
|   gRPC jsonimg	| 17.17 ms |  16.56 ms 	     |     221.45 ms    |
|   PING            |  0.14 ms |   0.25 ms  |     141.8 ms     |

You should measure the basic latency  using the `ping` command - this can be construed to be the latency without any RPC or python overhead.

You should examine your results and provide a short paragraph with your observations of the performance difference between REST and gRPC. You should explicitly comment on the role that network latency plays -- it's useful to know that REST makes a new TCP connection for each query while gRPC makes a single TCP connection that is used for all the queries.


# Timing explanation 

gRPC in most cases is much quicker compared to REST calls. The primary reason for this is because gRPC relies on HTTP/2 protocol whereas REST utilizes HTTP/1. The advantage of HTTP/2 being that it offers multiplexed streams, allowing the clients to send multiple requests without establishing a new TCP connection. In case of REST and HTTP/1 a new TCP connection is established for each query. Creating a new TCP connection for every request creates an additional overhead. Another advantage that gRPC has over REST is that it uses Protocol buffers for communication rather than the text based format (JSON, XML) in REST. Since the Protocol buffer transmits the data in binary format is it a lot quicker to serialize and deserialize the data. Moreover, it being a strongly typed format leads to lesser parsing errors. 

The results of the test conducted are shown in the above table. The base network latency increases from localhost to same-zone to different-zone.Due to this reason the average time taken to complete a call with client and server in different zones is significantly higher than localhost and same-zone, with same-zone being slightly higher than localhost. Moreover, for almost all the calls the gRPC calls are faster than the REST calls expect for rawImage in localhost and same-zone. 