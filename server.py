# import required libraries & proto defn.
import grpc
from concurrent import futures

from proto import asr_pb2_grpc
import time
# import servicer
from servicers import ASRServicer

URI = 'localhost:50051'    # Endpoint



def serve():
    # initialize server with 4 workers
    fts = futures.ThreadPoolExecutor(max_workers=4)
    server = grpc.server(fts)

    # attach servicer method to the server
    asr_pb2_grpc.add_ASRServicer_to_server(ASRServicer(), server)

    # start the server on the port 50051
    server.add_insecure_port(URI)
    server.start()
    print(f"Started gRPC server:{URI}")

    # server loop to keep the process running
    server.wait_for_termination()
 


# invoke the server method
if __name__ == "__main__":
    try:
        serve()
    except:
        pass