from threading import Thread

import time

import datetime

import Sensor as sensor
import numpy as np

import json

def task(sensor, wav_file, conf_file, real):
    y_true, y_pred = [], []
    sleepTime = 0.9*sensor.frameSize

    sensor.dataPre.wavSegmentation(wav_file, sensor.frameSize)

    y_true = sensor.model.createTestLabel(conf_file, sensor.frameSize, len(sensor.dataPre.chunkList), real)

    for i in range(len(sensor.dataPre.chunkList)):
        wav_chunk = "./out/wav/chunk" + str(i) + ".wav"

        # start_time = time.time()
        sample = sensor.dataPre.FeatureExtraction(wav_chunk)
        # elapsed_time = time.time() - start_time
        # print("Elapsed time: " + str(elapsed_time))
        sample = np.array(sample)

        # start_time = time.time()
        prediction = sensor.model.pipeline.pipeline.predict(sample.reshape(1, -1))
        # elapsed_time = time.time() - start_time
        # print("Elapsed time: " + str(elapsed_time))

        # print('chunk '+str(i)+": predicted --> "+str(prediction[0])+" expected --> "+str(y_true[i]))

        y_pred = y_pred + list(prediction)

        # if y_pred[-1] in [0, 1, 2]:
        #     alarm = {}
        #     alarm['sensorId'] = sensor.sensorId
        #     alarm['type'] = str(prediction[0])
        #     ts = time.time()
        #     isodate = datetime.datetime.fromtimestamp(ts, None)
        #     alarm['timestamp'] = str(isodate)
        #
        #     json_data = json.dumps(alarm)
        #
        #     sensor.socket.mysend(bytearray(json_data, 'utf8'))
        #
        # time.sleep(sleepTime)

    return y_true, y_pred


def sensor_thread(sensor, datasetPath, wavRange, snrRange, real):
    y_true, y_pred = [], []

    # for i in wavRange:  # process all wav
    #     if i < 10:
    #         conf_file = datasetPath + '0000' + str(i) + '.xml'
    #         wav_base_path = datasetPath + 'sounds/0000' + str(i)
    #     else:
    #         conf_file = datasetPath + '000' + str(i) + '.xml'
    #         wav_base_path = datasetPath + 'sounds/000' + str(i)
    #
    #     for j in snrRange:  # process differents snr  1=5db ... 6=30db
    #         wav_file = wav_base_path + '_' + str(j) + '.wav'
    #         print('Processing ' + wav_file[-26:])
    #         tmp_true, tmp_pred = task(sensor, wav_file, conf_file, real)
    #         y_true = y_true + tmp_true
    #         y_pred = y_pred + tmp_pred
    #
    # sensor.model.evaluate(y_true, y_pred, real)

    for j in snrRange:  # process differents snr  1=5db ... 6=30db
        y_true, y_pred = [], []
        for i in wavRange:  # process all wav
            if i < 10:
                conf_file = datasetPath + '0000' + str(i) + '.xml'
                wav_base_path = datasetPath + 'sounds/0000' + str(i)
            else:
                conf_file = datasetPath + '000' + str(i) + '.xml'
                wav_base_path = datasetPath + 'sounds/000' + str(i)

            wav_file = wav_base_path + '_' + str(j) + '.wav'
            print('Processing ' + wav_file[-26:])
            tmp_true, tmp_pred = task(sensor, wav_file, conf_file, real)
            y_true = y_true + tmp_true
            y_pred = y_pred + tmp_pred

        sensor.model.evaluate(y_true, y_pred, real)


if __name__ == "__main__":
    sensor = sensor.Sensor(id='93-19-25-1F-2A-21', host='127.0.0.1', port=1336)

    real = True
    datasetPath = '/home/valerio/Scrivania/stage/dataset/MIVIA_DB4_dist/testing/'
    wavRange = range(1, 30)  # range(1, 30) to process all testing dataset
    snrRange = [1, 2, 3, 4, 5, 6]  # range(1, 7) to process all snr

    thread = Thread(target=sensor_thread, args=(sensor, datasetPath, wavRange, snrRange, real))

    print("\nthread started...\n")
    start_time = time.time()
    thread.start()
    thread.join()
    elapsed_time = time.time() - start_time
    print("Elapsed time: " + str(elapsed_time))
    print("\nthread finished...exiting\n")