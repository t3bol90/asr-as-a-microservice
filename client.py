# import required libraries & proto defn.
import grpc
from proto import asr_pb2_grpc, asr_pb2

# non-ref
import pyaudio



from multiprocessing import Queue

import sys
import time
# Loot dạo từ để có tri thức nghiệp vụ: https://viettelgroup.ai/document/grpc 

CHUNK = 8000    # Length of bytebuff
CHANNELS = 1    # Number channel of audio
RATE = 16000    # Sample rate of audio (Hz)

_TIMEOUT_SECONDS_STREAM = 10000 # Time of out request from client to server

URI = 'localhost:50051'    # Endpoint
FILE = 'audio/sample.wav'   # Audio file

import logging
logname = "logs/clients.txt"
FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename=logname,
                    filemode='a')
logger = logging.getLogger('ClientSender')

import _thread as thread
import threading

def record_block():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    while True:
        block = stream.read(CHUNK)
        block_audio = asr_pb2.VoiceRequest(byte_buff=block)
        yield block_audio
        # time.sleep(0.1*CHUNK/3072.0)


def read_block():
    with open(FILE, 'rb') as rd:   
        while True:
            block = rd.read(CHUNK)   
            if len(block) == 0:
                break
            block_audio = asr_pb2.VoiceRequest(byte_buff=block)
            yield block_audio
            # time.sleep(0.1*CHUNK/3072.0)



def run():
    metadata = [('channels', str(CHANNELS)), ('rate', str(RATE)), ('single_sentence', str(SINGLE_SENTENCE)), ('token', 'test_token'), ('id', 'test_id')]
    channel = grpc.insecure_channel(target=URI)
    stub = asr_pb2_grpc.ASRStub(channel=channel)
    try:
        if FILE != '':
            responses = stub.workerSpeechToText(read_block(), timeout=_TIMEOUT_SECONDS_STREAM, metadata=metadata)
        else:
            responses = stub.workerSpeechToText(record_block(),timeout=_TIMEOUT_SECONDS_STREAM, metadata=metadata)
        
        # time.sleep(10)


        for response in responses:
            if response.status == 1:
                sentence = response.result.transcript
                if response.result.final:
                    print("Result: {}".format(sentence))
                else:
                    if len(sentence) > 100:
                        sentence = "..." + sentence[-100:]
                    print("-----: {}".format(sentence), end='')
            else:
                print(response.msg)
    except:
        e = sys.exc_info()[0]
        logger.error('%s: Client error: %s', e)


if __name__ == "__main__":
    try:
        run()
    except:
        pass

    
