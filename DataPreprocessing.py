from FeaturesExtraction import audioFeatureExtraction, audioBasicIO
import numpy as np
from pydub import AudioSegment


class DataPreprocessing:

    def __init__(self):
        self.subframeSize = 0.150
        self.subframeOverlap = 0.075
        self.discard = 21

    def wavSegmentation(self, filename, frameSize, gui=False):
        audio = AudioSegment.from_file(filename, "wav")

        self.chunkList = []
        curPos = 0
        N = len(audio)
        Win = int(frameSize * 1000)   # pydub calculates in millisec
        Step = int(Win * 0.5)
        i = 0

        while curPos + Win - 1 < N:
            chunk = audio[curPos:curPos + Win]

            self.chunkList.append(chunk)

            chunk_name = "chunk{0}.wav".format(i)
            if gui:
                chunk.export("../out/wav/" + chunk_name, format="wav")
            else:
                chunk.export("./out/wav/" + chunk_name, format="wav")

            curPos = curPos + Step
            i += 1

    def FeatureExtraction(self, wav_chunk):
        [Fs, signal] = audioBasicIO.readAudioFile(wav_chunk)

        Win = self.subframeSize * Fs
        Step = self.subframeOverlap * Fs

        F = audioFeatureExtraction.stFeatureExtraction(signal, Fs, Win, Step)

        raw_feature = F[:self.discard, :].T

        tmp = []
        for j in range(0, raw_feature.shape[1]):  # compute median and med for each columns
            feature_column = raw_feature[:, j]
            median = np.median(raw_feature[:, j])
            median_absolute_deviation = np.median(np.abs(feature_column - median))
            tmp.append(median)
            tmp.append(median_absolute_deviation)
        features = tmp

        return features