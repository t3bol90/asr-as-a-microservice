# import required libraries & proto defn.
import grpc
from concurrent import futures
from proto import sample_pb2_grpc

# import servicer
from servicers import SampleServiceServicer

def serve():
    # initialize server with 4 workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

    # attach servicer method to the server
    sample_pb2_grpc.add_SampleServiceServicer_to_server(SampleServiceServicer(), server)

    # start the server on the port 50051
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("Started gRPC server: 0.0.0.0:50051")

    # server loop to keep the process running
    server.wait_for_termination()


# invoke the server method
if __name__ == "__main__":
    serve()