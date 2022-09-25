# import required libraries & proto defn.
from proto import asr_pb2_grpc, asr_pb2
import uuid
from datetime import datetime

import sys
import wave
import wenetruntime as wenet
import time

import logging

FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SpeechToText')

QUEUE_SIZES = 100

# FWIW: https://stackoverflow.com/questions/11288158/python-iterable-queue

class IterableQueue():
	''' An iterator over queue data structure that
		stops when the predicate is false
	'''
	def __init__(self, Q, num_asrs):
		self.Q = Q
		self.endcount = 0
		self.num_asrs = num_asrs
		self.predicate = True

	def __iter__(self):
		return self

	def _check(self, x):
		if x['final'] == True:
			self.endcount += 1

		if self.endcount == self.num_asrs:
			self.predicate = False

	def next(self):
		if self.predicate:
			item = self.Q.get()
			self._check(item)
			return item
		else:
			raise StopIteration


class ASRServicer(asr_pb2_grpc.ASRServicer):
    ''' this servicer method will read the request from the iterator supplied
        by incoming stream and send back the response in a stream
    '''
    def __init__(self):
        self.decoder = wenet.Decoder(lang='en')
        logger.info("ASRServicer initializaiton finised")

    def speech_regconize(self, chunks):
        # start = time.time()
        # # We suppose the wav is 16k, 16bits, and decode every 0.5 seconds
        # interval = int(0.1 * 16000) * 2
        # for i in range(0, len(wav), interval):
        #     last = False if i + interval < len(wav) else True
        #     chunk_wav = wav[i: min(i + interval, len(wav))]
            # ans = decoder.decode(chunk_wav, last)
        pass

	def _splitStream(self, request_iterator, listQueues, config):
		''' Place the items from the request_iterator into each
			queue in the list of queues. When using VAD (continuous
			= True), the end-of-speech (EOS) can occur when the
			stream ends or inactivity is detected, whichever occurs
			first.
		'''
		counter = 0

		for chunk in request_iterator:
			counter += 1

			for Q in listQueues:
				Q.put(chunk.content)

		for Q in listQueues:
			# logger.info('adding end of speech')
			Q.put('EOS')

    def workerSpeechToText(self, request_iterator, context):
        # entry_info = dict()
        # for request in request_iterator:
        #     # print(request)
        #     print(request.byte_buff)
        #     ##### save to database #####
        #     # chunks = request.byte_buff
            
        #     text_reply = {
        #         "status": 1,
        #         "msg": "chao em",
        #         "id": str(uuid.uuid4()),
        #         "result": {"final": True, "transcript": "Con co be be"}
        #     }

        #     # stream the response back
        #     yield asr_pb2.TextReply(**text_reply)


        all_queues = []
		for _ in range(QUEUE_SIZES):
			all_queues.append(Queue.Queue())

        # CHUNKS DB
		all_queues.append(Queue.Queue())

		logger.debug('%s: Runin')

		thread_ids = []

		t = threading.Thread(target=self._splitStream, args=(request_iterator, all_queues, config))
		t.start()
		thread_ids.append(t)
		t = threading.Thread(target=LogStream, args=(iter(all_queues[-1].get, 'EOS'), token))
		t.start()
		thread_ids.append(t)

		responseQueue = Queue.Queue()
		# for ix, asr in enumerate(config['asrs']):
        #     gw = google.worker(token)
        #     t = threading.Thread(target=self._mergeStream, args=
        #         (gw.stream(iter(all_queues[ix].get, 'EOS'), config),
        #             responseQueue, asr))
        #     t.start()
        #     thread_ids.append(t)


		# keep sending transcript to client until *all* ASRs are DONE
		for item_json in IterableQueue(responseQueue, len(config['asrs'])):

			# logger.info(item_json)
			if item_json['is_final']:

				each_record = {}
				each_record['asr'] = item_json['asr']
				each_record['transcript'] = item_json['transcript']
				each_record['is_final'] = item_json['is_final']
				each_record['confidence'] = 1.0
				record['results'].append(each_record)

				# WE DONOT JOIN
				# for t in thread_ids:
				# 	t.join()

			#TODO: write each record to DB separately because the client
			#may break the call after just one ASR finishes
			yield stt_pb2.TranscriptChunk(
				asr = item_json['asr'],
				transcript = item_json['transcript'],
				is_final = item_json['is_final'],
				confidence = 1.0,
				)

		try:
			self._write_to_database(record)
		except:
			e = sys.exc_info()[0]
			logger.error('%s: Database error: %s', token, e)

