'''
strates how to use `CNN` model from
`speechemotionrecognition` package
'''
from keras.utils import np_utils

import pulsectl
import serial
import time
import os
import sys
import collections
import webrtcvad
import signal
import subprocess
import socket as sk
import numpy as np
from common import extract_data
from dnn_test import CNN, LSTM
from utilities_test import get_feature_vector_from_mfcc, get_stream_feature_vector_from_mfcc
from pywebrtcvad.vadfunc import make_chunk, make_stream_chunk, write_wave, frame_generator, stream_vad_collector

pulse = pulsectl.Pulse('my-client-name')

def give_me_the_device_num():
    source_list = pulse.source_list()
    for row in source_list:
        if str(row).find('bluez') != -1:
            chunk = str(row).split(' ')
            for cc in chunk:
                idx = cc.find('index=')
                if idx != -1:
                    return cc[6:-1]
    return -1


def recording_blue(rate, device_num):
    cmd = "parec -r --rate=" + str(rate) + " --device=" + str(device_num) + " --channels=1"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                       shell=True, preexec_fn=os.setsid)
    return process

def lstm_example():
    # initializing dont touch
    timeout = False
    trigger_num = 0
    ser_to_ino = serial.Serial('/dev/ttyUSB0', 9600)
    file_idx = 0
    rate = 16000
    duration_sec = 4
    duration_byte = rate * 2 * duration_sec

    to_flatten = False
    in_shape = np.zeros((198,39))
    model = LSTM(input_shape=in_shape.shape, num_classes=7)

    load_path = 'korean_LSTM_best_model.h5'
    model.load_model(load_path)
    model.trained = True

    print('start')
    device_num = give_me_the_device_num()
    print("device_num: ", device_num)
    process = recording_blue(rate, device_num)

    pcm_list = []

    aggressive = 3
    triggered = False
    padding_duration_ms = 300
    frame_duration_ms = 30
    n = int(rate * (frame_duration_ms / 1000.0) * 2)
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    vad = webrtcvad.Vad(aggressive)
    voiced_frames = []

    sibal_idx = 0
    while(1):
        pcm_data_line = process.stdout.readline()
        # pcm_data += pcm_data_line
        pcm_list.append(pcm_data_line)
        # target_num = len(pcm_data) // n # number of audio data for 30 milli seconds
        target_num = len(pcm_list)
        if target_num <= 300:
            continue

        pcm_data = b''.join(pcm_list)
        sibal_idx += 1

        target_num = len(pcm_data) // n
        pcm_data_to_chunk = pcm_data[:n * target_num]
        pcm_list = [pcm_data[n * target_num:]]
        # pcm_data = pcm_data[n * target_num:]

        frames = list(frame_generator(frame_duration_ms, pcm_data_to_chunk, rate))
        for frame in frames:
            triggered, voiced_audio, timeout = stream_vad_collector(rate, vad, frame, triggered, ring_buffer, voiced_frames, timeout)
            if triggered and not timeout:
                trigger_num += 1
                if 150 <= trigger_num: # 150 means 4.5 seconds
                    timeout = True

            if voiced_audio is not None: # talking -> no talking then this if works.
                trigger_num = 0
                voiced_frames = []
                emotion = model.predict_one(get_stream_feature_vector_from_mfcc(voiced_audio, fs=rate, flatten=to_flatten))
                print(emotion)
                ser_to_ino.write(str(emotion).encode('utf-8'))
                file_idx += 1

if __name__ == "__main__":
    lstm_example()

