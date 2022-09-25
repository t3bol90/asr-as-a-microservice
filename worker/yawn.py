# Yet Another WeNet

import sys
import wave
import wenetruntime as wenet
import time

# worker test
# import utils

# test_wav = sys.argv[1]

# with wave.open(test_wav, 'rb') as fin:
#     assert fin.getnchannels() == 1
#     wav = fin.readframes(fin.getnframes())

# decoder = wenet.Decoder(lang='en')

# start = time.time()
# # We suppose the wav is 16k, 16bits, and decode every 0.5 seconds
# interval = int(0.1 * 16000) * 2
# for i in range(0, len(wav), interval):
#     last = False if i + interval < len(wav) else True
#     chunk_wav = wav[i: min(i + interval, len(wav))]
#     ans = decoder.decode(chunk_wav, last)
#    # print(ans)
# end = time.time()
# print(end - start)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Audio recording parameters
RATE = 16000


import json

DECODER = wenet.Decoder(lang='en',enable_timestamp=False)

class worker:
    def __init__(self, token):
        self.decoder = DECODER
    def stream(self, chunkIterator, config=None):
        last = False
        ans = ""
        try:
            for chunk in chunkIterator:
                ans = self.decoder.decode(chunk, last)

                if not ans:
                    continue
                ans = json.loads(ans)

                temporal_result = {"transcript": ans['nbest'][0]['sentence'], "final": last}
                last = ans["type"] != "partial_result"
                yield temporal_result
                break
        
        except:
            e = sys.exc_info()[0]
            logger.error('%s: %s connection error', e)
        finally:
            if ans:
                last = True
                final_result = {"transcript": ans['nbest'][0]['sentence'], "final": last}
                yield final_result



# worker test

# if __name__ == '__main__':

#    W = worker('142857')
#    responses = W.stream(utils.generate_chunks("/root/asr-as-a-microservice/audio/sample.wav", grpc_on=False,
#        chunkSize=3072))
#    for response in responses:
#     print(response)