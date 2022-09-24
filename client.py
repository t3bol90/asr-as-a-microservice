# import required libraries & proto defn.
import grpc
from proto import sample_pb2_grpc, sample_pb2

# initialize channel to gRPC server
channel = grpc.insecure_channel(target="localhost:50051")

# create service stub
stub = sample_pb2_grpc.SampleServiceStub(channel=channel)

# define request object generator which will yield 15 requests
def entry_request_iterator():
    for idx in range(1, 16):
        entry_request = sample_pb2.EntryCreateRequest(title=f"Test {idx}", 
                                                        code=f"T{idx}",
                                                        description=f"Test {idx} description")
        yield entry_request

# iterate through response stream and print to console
for entry_response in stub.createBulkEntries(entry_request_iterator()):
    print(entry_response)
