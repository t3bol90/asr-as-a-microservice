# import required libraries & proto defn.
from proto import asr_pb2_grpc, asr_pb2
import uuid
from datetime import datetime

import sys
import wave
import wenetruntime as wenet
import time

import logging


logname = "logs/log.txt"
FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename=logname, filemode='a')
logger = logging.getLogger('ASRServicer')


from multiprocessing import Queue
import _thread as thread
import threading

# VAD
import webrtcvad

from collections import deque

RESPONSIVE_TIMEOUT = 1000  # milisec
CLIENT_ROUNTINE = 100  # milisec


CHUNK = 1600    # Length of bytebuff
CHANNELS = 1    # Number channel of audio
RATE = 16000    # Sample rate of audio (Hz)
INACTIVE_THRES = 2000

QUEUE_SIZES = 1
SLEEP_DELAY = 0.001

from worker import yawn


class ASRServicer(asr_pb2_grpc.ASRServicer):
    ''' this servicer method will read the request from the iterator supplied by incoming stream and send back the response in a stream
    '''
    def __init__(self):
        logger.info("ASRServicer initializaiton finised")
        self.vad = webrtcvad.Vad(3)

    def _mergeStream(self, asr_response_iterator, responseQueue, config):
        ''' Place the item from the asr_response_iterator of asr into a queue
        '''

        for asr_response in asr_response_iterator:
            responseQueue.put(asr_response)
        return


    def workerSpeechToText(self, request_iterator, context):
        '''
        Request interator handler
        '''
        counter = 0
        pref_chunks = (RESPONSIVE_TIMEOUT//CLIENT_ROUNTINE)*10
        final = False
        responseQueue = Queue()
        inputQueue = Queue()

        config = {}
        curr_buff = b""

        inact_frame = INACTIVE_THRES//(RESPONSIVE_TIMEOUT//10 * 32)
        buffer = deque(maxlen=inact_frame)
        frame_bytes = 320 # RATE*2*frame_size

        for chunk in request_iterator:
            
            n = len(chunk.byte_buff)
            curr_vad = chunk.byte_buff
            offset = 0

            while n >= frame_bytes:
                is_speech = self.vad.is_speech(curr_vad[offset:offset+frame_bytes], RATE)
                buffer.append(is_speech)
                n = n - frame_bytes
                offset += frame_bytes
                
            num_voiced = len([f for f in buffer if f is True])
            if num_voiced < 0.1*buffer.maxlen:
                continue

            

            counter += 1
            curr_buff += chunk.byte_buff
            if (counter == pref_chunks):
                logger.info("Send chunk to worker")
                
                counter = 0
                
                worker_node = yawn.worker(str(uuid.uuid4()))
                inputQueue.put(curr_buff)

                t = threading.Thread(target=self._mergeStream, args=(worker_node.stream(iter(inputQueue.get, 'EOS'), config), responseQueue, config))
                t.start()
                curr_buff = b''
                res = responseQueue.get()
                text_reply = {
                    "status": 1,
                    "msg": "",
                    "id": str(uuid.uuid4()),
                    "result": {"transcript": res["transcript"], "final": False}
                }

                try:                
                    logger.info(f"Reply {text_reply}")
                    yield asr_pb2.TextReply(**text_reply)

                except:
                    e = sys.exc_info()[0]
                    logger.error('%s: TextReply error: %s', e)
        if counter > 0:
            worker_node = yawn.worker(str(uuid.uuid4()))
            inputQueue.put(curr_buff)
            t = threading.Thread(target=self._mergeStream, args=(worker_node.stream(iter(inputQueue.get, 'EOS'), config), responseQueue, config))
            t.start()
            
            res = responseQueue.get()
            text_reply = {
                "status": 1,
                "msg": "MS_CODE",
                "id": str(uuid.uuid4()),
                "result": {"transcript": res["transcript"], "final": True}
            }
            
        else:
            text_reply = {
                "status": 1,
                "msg": "MS_CODE",
                "id": str(uuid.uuid4()),
                "result": {"transcript": "", "final": True}
            }
        try:                
        # stream the response back
            logger.info(f"Reply {text_reply}")
            yield asr_pb2.TextReply(**text_reply)

        except:
            e = sys.exc_info()[0]
            logger.error('%s: TextReply error: %s', e)
