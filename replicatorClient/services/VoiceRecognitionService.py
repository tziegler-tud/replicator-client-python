import asyncio
import logging
import threading
from enum import Enum
from picovoice import Picovoice, PicovoiceError
from pvrecorder import PvRecorder

from .Service import Service, StatusEnum
from .VoiceCommandService import VoiceCommandService, Command


class VoiceRecognitionService(Service):

    instance = None

    @staticmethod
    def getInstance():
        if VoiceRecognitionService.instance is not None:
            return VoiceRecognitionService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if VoiceRecognitionService.instance is not None:
            return VoiceRecognitionService.instance
        else:
            VoiceRecognitionService.instance = VoiceRecognitionService()


    def __init__(self, **kwargs):
        super().__init__()
        self.name = "VoiceRecognitionService"
        self.recorderDeviceIndex = kwargs.get('recorderDeviceIndex', -1)

        self.picovoiceConfig = self.settingsService.getVoiceConfig()

        VoiceRecognitionService.instance = self

    def addRecorder(self, recorderDeviceIndex):
        def keyword_callback():
            print("Wake word detected.")
            VoiceCommandService.processKeyword(self)

        def inference_callback(inference):
            print("Inference: " + str(inference))


            # threading.Thread(target=VoiceCommandService.processCommand, args=[inference]).start()
            self.main_loop.run_until_complete(VoiceCommandService.processCommandAsync(Command(inference.is_understood, inference.intent, inference.slots)))

        try:
            self.picovoice = Picovoice(
                access_key= self.picovoiceConfig['accessKey'],
                keyword_path= self.picovoiceConfig['keywordArgument'],
                wake_word_callback= keyword_callback,
                context_path=self.picovoiceConfig['contextPath'],
                inference_callback=inference_callback)
        except PicovoiceError as e:
            pass

        recorder = PvRecorder(
            frame_length=self.picovoice.frame_length,
            device_index= recorderDeviceIndex,
        )
        return recorder

    def initFunc(self):
        self.recorder = self.addRecorder(self.recorderDeviceIndex)
        def startRecorder():
            self.recorder.start()
            print("Listening for 'COMPUTER'")
            while self.recorder.is_recording:
                try:
                    frames = self.recorder.read()
                    self.picovoice.process(frames)
                except Exception as e:
                    logging.error("Error while reading recorder: " + e)

        if self.recorder is not None:
            t = threading.Thread(target=startRecorder, args=[])
            t.start()
        else:
            logging.error("Failed to start recorder: Recorder not initialized.")

        print("Not blocked!")
        return True

    def start(self, main_loop, *args):
        self.main_loop = main_loop
        self.debug("Starting Service: " + self.name)
        if self.status == StatusEnum.RUNNING:
            return True
        self.initStarted = True
        self.systemSettings = self.settingsService.getSettings()
        try:
            self.status = StatusEnum.RUNNING
            self.initFunc()
            return True
        except Exception as e:
            self.status = StatusEnum.FAILED
            self.debug("ERROR: Service startup failed: " + self.name)
            logging.error("ERROR: Service failed to start: " + self.name)
            return False


    def stopService(self):
        self.recorder.stop()

    def restart(self):
        print("Stopping VoiceRecognitionService....")
        self.stop()
        self.systemSettings = self.settingsService.getSettings()
        self.picovoiceConfig = self.settingsService.getPicovoiceConfig()
        print("Restarting VoiceRecognitionService....")

        try:
            self.start()
            return self.status
        except Exception as e:
            logging.error("Failed to restart VoiceRecognitionService: " + e)
