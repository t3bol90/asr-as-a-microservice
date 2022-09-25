# Yet Another WeNet

# import sys
# import wave
# import wenetruntime as wenet
# import time

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

# {
#   "nbest" : [{
#       "sentence" : "several tor"
#     }],
#   "type" : "partial_result"
# }


class worker:
    def __init__(self, token):
        pass
    def stream(self, chunkIterator, config=None):
        # parse command line parameters
        contentType = 'audio/l16; rate=16000'
        model = 'en-US_BroadbandModel'
        optOut = False

        hostname = "stream.watsonplatform.net"
        headers = {}

        if (optOut == True):
            headers['X-WDC-PL-OPT-OUT'] = '1'

        creds = get_credentials()
        string = creds['username'] + ":" + creds['password']
        headers["Authorization"] = "Basic " + base64.b64encode(string)

        url = "wss://" + hostname + "/speech-to-text/api/v1/recognize?model=" + model

        responseQueue = Queue.Queue()

        last_transcript = ''
        try:
            client = ASRClient(url, headers, chunkIterator, responseQueue, contentType, config)
            client.connect()
            logger.info("%s: Initialized", self.token)
            responseIterator =  iter(responseQueue.get, 'EOS')
            for response in responseIterator:
                last_transcript = response
                yield {'transcript' : last_transcript, 'is_final': False}
        except:
            e = sys.exc_info()[0]
            logger.error('%s: %s connection error', self.token, e)
        finally:
            yield {'transcript' : last_transcript, 'is_final': True}
            logger.info('%s: finished', self.token)


if __name__ == '__main__':

   # logging
   # log.startLogging(sys.stdout)
   parser = argparse.ArgumentParser()
   parser = argparse.ArgumentParser(description='speech recognition client interface to Watson STT service')
   parser.add_argument('-in', action='store', dest='filename', default='audio/test1.raw', help='audio file')
   args = parser.parse_args()

   W = worker('123456')
   responses = W.stream(utils.generate_chunks(args.filename, grpc_on=False,
       chunkSize=3072))
   for response in responses:
     print(response)