import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QUrl

import simulation_gui.design as design
import urllib.request
import json

import codecs

import time

import datetime

import Sensor
import numpy as np
import sys


class PlayThread(QThread):

    def __init__(self, datasetPath, wav, snr):
        QThread.__init__(self)
        self.datasetPath = datasetPath
        self.wav = wav
        self.snr = snr

    def __del__(self):
        self.wait()

    def play(self, path):
        url = QUrl.fromLocalFile(path)
        content = QMediaContent(url)
        self.player = QMediaPlayer()
        self.player.setMedia(content)
        self.player.play()

    def stop(self):
        self.player.stop()

    def run(self):
        if self.wav < 10:
            wav_base_path = self.datasetPath + 'sounds/0000' + str(self.wav)
        else:
            wav_base_path = self.datasetPath + 'sounds/000' + str(self.wav)

        path = wav_base_path + '_' + str(self.snr) + '.wav'
        self.play(path)
        QThread.exec(self)


class SimulationThread(QThread):
    update_bar = pyqtSignal(str)
    set_max = pyqtSignal(int)

    def __init__(self, sensor, real, datasetPath, wav, snr):
        QThread.__init__(self)
        self.sensor = sensor
        self.real = real
        self.datasetPath = datasetPath
        self.wav = wav
        self.snr = snr

    def __del__(self):
        self.wait()

    def task(self, sensor, wav_file, conf_file, real):
        y_true, y_pred = [], []
        sleepTime = 0.12 * sensor.frameSize

        sensor.dataPre.wavSegmentation(wav_file, sensor.frameSize, gui=True)

        y_true = sensor.model.createTestLabel(conf_file, sensor.frameSize, len(sensor.dataPre.chunkList), real)
        self.set_max.emit(len(y_true))

        last_event_time = time.time()
        for i in range(len(sensor.dataPre.chunkList)):
            wav_chunk = "../out/wav/chunk" + str(i) + ".wav"

            sample = sensor.dataPre.FeatureExtraction(wav_chunk)
            sample = np.array(sample)

            prediction = sensor.model.pipeline.pipeline.predict(sample.reshape(1, -1))

            print('chunk '+str(i)+": predicted --> "+str(prediction[0])+" expected --> "+str(y_true[i]))

            y_pred = y_pred + list(prediction)

            if y_pred[-1] in [0, 1, 2]:
                current_time = time.time()
                print(current_time)
                print(current_time-last_event_time)
                if current_time-last_event_time > 0.3:
                    current_event_time = datetime.datetime.fromtimestamp(current_time, None)
                    alarm = {}
                    alarm['timestamp'] = str(current_event_time)
                    alarm['sensorId'] = sensor.sensorId
                    alarm['type'] = str(prediction[0])
                    json_data = json.dumps(alarm)

                    sensor.socket.mysend(bytearray(json_data, 'utf8'))
                else:
                    print('discard\n')

                last_event_time = current_time

            time.sleep(sleepTime)
            self.update_bar.emit('update bar')

        sensor.model.evaluate(y_true, y_pred, real)

    def run(self):
        y_true, y_pred = [], []

        if self.wav < 10:
            conf_file = self.datasetPath + '0000' + str(self.wav) + '.xml'
            wav_base_path = self.datasetPath + 'sounds/0000' + str(self.wav)
        else:
            conf_file = self.datasetPath + '000' + str(self.wav) + '.xml'
            wav_base_path = self.datasetPath + 'sounds/000' + str(self.wav)

        wav_file = wav_base_path + '_' + str(self.snr) + '.wav'
        print('Processing ' + wav_file[-26:])
        tmp_true, tmp_pred = self.task(self.sensor, wav_file, conf_file, self.real)
        y_true = y_true + tmp_true
        y_pred = y_pred + tmp_pred

        print(y_true, y_pred)


class SimulationGui(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.btn_start.clicked.connect(self.start_simulation)

    def start_simulation(self):
        sensor = Sensor.Sensor(id='93-19-25-1F-2A-21', host='127.0.0.1', port=1336, gui=True)
        real = True
        datasetPath = '/home/valerio/Scrivania/stage/dataset/MIVIA_DB4_dist/testing/'

        wav = self.edit_file_id.text()
        snr = self.edit_snr.text()

        try:
            wav = int(wav)
            snr = int(snr)
        except Exception:
            QMessageBox.critical(self, 'Error', 'Input can only be a number', QMessageBox.Ok)
            return

        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        self.simulation_thread = SimulationThread(sensor, real, datasetPath, wav, snr)

        self.simulation_thread.update_bar.connect(self.update_bar)

        self.simulation_thread.set_max.connect(self.set_max)

        self.simulation_thread.finished.connect(self.done)

        self.simulation_thread.start()

        self.btn_stop.setEnabled(True)

        self.btn_stop.clicked.connect(self.simulation_thread.terminate)

        self.btn_start.setEnabled(False)

        self.play_thread = PlayThread(datasetPath, wav, snr)
        self.play_thread.start()

    def set_max(self, max):
        self.progress_bar.setMaximum(max)

    def update_bar(self):
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def done(self):
        self.play_thread.stop()     # TODO fix ... is a workaround
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(0)
        QMessageBox.information(self, "Done!", "Simulation completed!")


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = SimulationGui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()