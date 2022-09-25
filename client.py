# import required libraries & proto defn.
import grpc
from proto import asr_pb2_grpc, asr_pb2

# non-ref
import pyaudio

# Loot dạo từ để có tri thức nghiệp vụ: https://viettelgroup.ai/document/grpc 

CHUNK = 8000    # Length of bytebuff
CHANNELS = 1    # Number channel of audio
RATE = 16000    # Sample rate of audio (Hz)

URI = 'localhost:50051'    # Endpoint
FILE = 'audio/sample.wav'   # Audio file
SINGLE_SENTENCE = True  # If True, finish after recognizing 1 sentence. And keep recognizing if False

def record_block():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    while True:
        block = stream.read(CHUNK)
        block_audio = asr_pb2.VoiceRequest(byte_buff=block)
        yield block_audio

def read_block():
    with open(FILE, 'rb') as rd:   
        while True:
            block = rd.read(CHUNK)   
            if len(block) == 0:
                break
            block_audio = asr_pb2.VoiceRequest(byte_buff=block)
            yield block_audio



def run():
    metadata = [('channels', str(CHANNELS)), ('rate', str(RATE)), ('single_sentence', str(SINGLE_SENTENCE)), ('token', 'test_token'), ('id', 'test_id')]
    channel = grpc.insecure_channel(target=URI)
    stub = asr_pb2_grpc.ASRStub(channel=channel)
    try:
        if FILE != '':
            responses = stub.workerSpeechToText(read_block(), metadata=metadata)
        else:
            responses = stub.workerSpeechToText(record_block(), metadata=metadata)
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
        pass


if __name__ == "__main__":
    run()
