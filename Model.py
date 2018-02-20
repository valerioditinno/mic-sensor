from os import listdir
from os.path import isfile, join

import pandas as pd
from sklearn.externals import joblib

import xml.etree.ElementTree as et

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import seaborn as sn
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score

from BuilderPipeline.BuilderPipeline import BuilderPipeline


class Model(object):

    def __init__(self, gui):
        self.tolerance = 0.2
        self.eventCount = 0
        self.y_trans = []  # index of labels related to transitory events
        self.pipeline = BuilderPipeline()

        self.cont = 0

        if gui:
            path_class = "../model/Classifier/"
            path_fs = "../model/FeatureSelection/"
            path_scaler = "../model/Scaler/"
        else:
            path_class = "./model/Classifier/"
            path_fs = "./model/FeatureSelection/"
            path_scaler = "./model/Scaler/"

        if len(listdir(path_class)) > 1:
            classifiers = {f.replace(".pkl", "").split("_")[1]: joblib.load(path_class + f)
                           for f in listdir(path_class) if isfile(join(path_class, f))}
            self.pipeline.clf = classifiers
        else:

            if isfile(join(path_class, listdir(path_class)[0])):
                classifiers = joblib.load(path_class + listdir(path_class)[0])
                self.pipeline.clf = classifiers

        if len(listdir(path_fs)) > 1:
            fs = {f.replace(".pkl", "").split("_")[1]: joblib.load(path_fs + f) for f in listdir(path_fs) if isfile(join(path_fs, f))}
            self.pipeline.feature_selection = fs

        elif listdir(path_fs):
            if isfile(join(path_fs, listdir(path_fs)[0])):
                fs = joblib.load(path_fs + listdir(path_fs)[0])
                self.pipeline.feature_selection = fs
        else:
            self.pipeline.feature_selection = {}

        if len(listdir(path_scaler)) > 1:
            sc = {f.replace(".pkl", "").split("_")[1]: joblib.load(path_scaler + f) for f in listdir(path_scaler) if isfile(join(path_scaler, f))}
            self.pipeline.scaler = sc

        elif listdir(path_scaler):
            if isfile(join(path_scaler, listdir(path_scaler)[0])):
                sc = joblib.load(path_scaler + listdir(path_scaler)[0])
                self.pipeline.scaler = sc

    def parseXml(self, filename):
        tree = et.parse(filename)
        root = tree.getroot()

        eventsList = []
        for i in root.findall("./events/item"):
            event = []
            className = i.find('CLASS_NAME').text
            if (className.startswith("glass")):
                target = "0"
            elif (className.startswith("gunshots")):
                target = "1"
            else:
                target = "2"
            event.append(target)
            start = i.find('STARTSECOND').text
            event.append(start)
            stop = i.find('ENDSECOND').text
            event.append(stop)

            eventsList.append(event)

        return eventsList

    def createTestLabel(self, filename, frameSize, numChunk, real):  # TODO check all correct
        eventsList = self.parseXml(filename)
        y_true = []

        if real:
            i = 0.0
            for event in eventsList:
                start = float(event[1])
                stop = float(event[2])

                while i < stop:
                    if i + frameSize < start:
                        y_true.append(int("3"))
                    elif i + frameSize >= start and i <= stop:
                        y_true.append(int(event[0]))
                    else:
                        y_true.append(int("3"))

                    self.eventCount += 1
                    i += frameSize * 0.5

            cont = numChunk - len(y_true)
            for i in range(cont):
                y_true.append(int("3"))
                self.eventCount += 1
        else:
            i = 0.0
            for event in eventsList:
                start = float(event[1])
                stop = float(event[2])

                while i < stop:
                    if i + frameSize - self.tolerance*frameSize < start:
                        y_true.append(int("3"))
                        if i + frameSize >= start:  # debug
                            self.cont += 1
                    elif i + self.tolerance*frameSize >= start and i + frameSize - self.tolerance*frameSize <= stop:
                        y_true.append(int(event[0]))
                    else:
                        y_true.append(int("3"))
                        if not(i + self.tolerance*frameSize > stop):  # drop frame
                            self.y_trans.append(self.eventCount)
                        elif i + self.tolerance*frameSize > stop:  # debug
                            self.cont += 1

                    self.eventCount += 1
                    i += frameSize*0.5

            cont = numChunk - len(y_true)
            for i in range(cont):
                y_true.append(int("3"))
                self.eventCount += 1

        return y_true

    def removeTransitoryLabels(self, y_true, y_pred):
        tmp_true, tmp_pred = [], []
        for i in range(0, len(y_true)):
            if i not in self.y_trans:
                tmp_true.append(y_true[i])
                tmp_pred.append(y_pred[i])

        y_true, y_pred = tmp_true, tmp_pred

        return y_true, y_pred

    def removeBias(self, y_true, y_pred):  # TODO check all correct
        # We count a false positive when an event of interest is
        # erroneously detected in a time window that contains only background noise;
        # if in two consecutive time windows a foreground event is detected,
        # we count a single false positive occurrence
        for i in range(0, len(y_true)-1):
            if (y_true[i] == 3 and y_true[i+1] == 3) and (y_pred[i] == y_pred[i+1] != 3):
                y_pred[i] = 3

        # An event is considered as correctly detected if it is detected in at
        # least one of the sliding time windows that overlap with it occurrence
        tmp_true, tmp_pred = [], []
        i = 0
        while i < len(y_true):
            if y_true[i] == 3:
                tmp_true.append(y_true[i])
                tmp_pred.append(y_pred[i])
                i += 1
            else:
                detected = False
                error_0, error_1, error_2, error_3 = 0, 0, 0, 0
                while y_true[i] != 3:
                    if y_true[i] == y_pred[i]:
                        detected = True
                        true = y_true[i]
                        pred = y_pred[i]
                    elif y_pred[i] == 0:
                        error_0 += 1
                    elif y_pred[i] == 1:
                        error_1 += 1
                    elif y_pred[i] == 2:
                        error_2 += 1
                    elif y_pred[i] == 3 and not (y_true[i-1] == 3 or y_true[i+1] == 3):
                        error_3 += 1
                    i += 1

                # debug
                # if not detected:
                #     print('true: ', y_true[i-6], y_true[i-5], y_true[i-4], y_true[i-3], y_true[i-2], y_true[i-1], y_true[i])
                #     print('pred: ', y_pred[i-6], y_pred[i-5], y_pred[i-4], y_pred[i-3], y_pred[i-2], y_pred[i-1], y_pred[i])
                #     print('error: ', error_0, error_1, error_2, error_3, "\n")

                error = max(error_0, error_1, error_2, error_3)
                if detected:
                    tmp_true.append(true)
                    tmp_pred.append(pred)
                elif error == error_0:
                    tmp_true.append(y_true[i-1])
                    tmp_pred.append(0)
                elif error == error_1:
                    tmp_true.append(y_true[i-1])
                    tmp_pred.append(1)
                elif error == error_2:
                    tmp_true.append(y_true[i-1])
                    tmp_pred.append(2)
                else:
                    tmp_true.append(y_true[i-1])
                    tmp_pred.append(3)

        y_true, y_pred = tmp_true, tmp_pred

        return y_true, y_pred

    def evaluate(self, y_true, y_pred, real):
        if real:
            y_true, y_pred = self.removeBias(y_true, y_pred)

            print("-" * 20)

            print("Confusion Matrix:")

            conf_mat = confusion_matrix(y_true, y_pred)

            index = ('True {}'.format(c) for c in np.unique(y_pred) if c is not None)
            columns = ('Pred {}'.format(c) for c in np.unique(y_pred) if c is not None)
            confmat_df = pd.DataFrame(data=conf_mat, index=index, columns=columns)

            print(confmat_df)

            plt.figure(figsize=(7, 5))
            sn.heatmap(confmat_df, annot=True, fmt="d", linewidths=.5, cmap="coolwarm", square=True)
            title = "Confusion Matrix"
            plt.title(title)
            plt.pause(1)

            print("-" * 20)
        else:
            y_true, y_pred = self.removeTransitoryLabels(y_true, y_pred)

            print("-" * 20)
            print("Tolerated frame: {}".format(self.cont))
            print("Data test metrics:")
            print("Removed transitory events: {}".format(len(self.y_trans)))
            print("None value number: {}".format(len([elem for elem in y_pred if elem is None])))

            target_names = ["class {}".format(target) for target in np.unique(y_true)]

            print("\n")
            print(classification_report(y_true, y_pred, target_names=target_names))
            print("\n")

            print("Confusion Matrix:")

            acc = accuracy_score(y_true, y_pred)
            conf_mat = confusion_matrix(y_true, y_pred)

            index = ('True {}'.format(c) for c in np.unique(y_pred) if c is not None)
            columns = ('Pred {}'.format(c) for c in np.unique(y_pred) if c is not None)
            confmat_df = pd.DataFrame(data=conf_mat, index=index, columns=columns)

            print(confmat_df)
            print("\nAccuracy : {}".format(acc))
            print("-" * 20)

            # plt.figure(figsize=(7, 5))
            # sn.heatmap(confmat_df, annot=True, fmt="d", linewidths=.5, cmap="coolwarm", square=True)
            # plt.title("Confusion Matrix")
            # plt.show()