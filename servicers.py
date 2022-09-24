# import required libraries & proto defn.
from proto import sample_pb2_grpc, sample_pb2
import uuid
from datetime import datetime

class SampleServiceServicer(sample_pb2_grpc.SampleServiceServicer):
    ''' this servicer method will read the request from the iterator supplied
        by incoming stream and send back the response in a stream
    '''
    def createBulkEntries(self, request_iterator, context):
        entry_info = dict()
        for request in request_iterator:
            print(request)

            ##### save to database #####

            # simulate the response after saving to database
            entry_info = {
                "id": str(uuid.uuid4()),
                "title": request.title,
                "code": request.code,
                "description": request.description,
                "created_on": round(datetime.now().timestamp())
            }

            # stream the response back
            yield sample_pb2.EntryResponse(**entry_info)
