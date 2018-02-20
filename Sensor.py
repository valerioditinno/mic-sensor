import Model as model
import Socket
import DataPreprocessing as dataPre


class Sensor:
    '''
        This class simulate a microphone sensor.
        It creates a Thread that:
        -create chunks of frameSize from the wav files of the MIVIA testing dataset using pydub library
        -periodically extract features from each chunk and call the predict of the classifier model
        -if detects an alarm("Scream", "Gunshot" or "Glass") send an alarm msg to the tcp/ip proxy


        [0 == glass, 1 == gunshots, 2 == screams, 3 ==  other]

        Example of alarm raised from sensor:
        {
            "sensorId": "93-19-25-1F-2A-21",
            "type": "0",
            "timestamp": "1829202302940920"

        }

    '''

    def __init__(self, id, host, port, gui=False):
        self.sensorId = id
        self.socket = Socket.MySocket(host=host, port=port)
        self.frameSize = 0.300
        self.dataPre = dataPre.DataPreprocessing()
        self.model = model.Model(gui)