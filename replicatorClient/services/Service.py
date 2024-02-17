import asyncio
import logging
from enum import Enum
from .SettingsService import SettingsService



class Service:
    instance = None

    @staticmethod
    def getInstance():
        if Service.instance is not None:
            return Service.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if Service.instance is not None:
            return Service.instance
        else:
            Service.instance = Service()

    def __init__(self):
        self.name = "unidentified Service"
        self.status = StatusEnum.NOTSTARTED

        self.init = asyncio.Future()

        self.systemSettings = None
        self.debugLabel = "Service: "
        self.enableDebug = True

        self.settingsService = SettingsService.getInstance()
        Service.instance = self

    def debug(self, message, level = 0):
        if self.settingsService.getSettings()["system"]["debugLevel"] <= level: print(self.debugLabel + message)

    def initFunc(self, *args):
        return True

    def start(self, *args):
        self.debug("Starting Service: " + self.name)
        if self.status == StatusEnum.RUNNING:
            return True
        self.initStarted = True
        self.systemSettings = self.settingsService.getSettings()
        try:
            self.status = StatusEnum.RUNNING
            self.initFunc(args)
            return True
        except Exception as e:
            self.status = StatusEnum.FAILED
            self.debug("ERROR: Service startup failed: " + self.name)
            logging.error("ERROR: Service failed to start: "+ self.name)
            return False

    def stop(self):
        self.debug("Stopping Service: " + self.name)
        try:
            self.stopService()
        except:
            self.debug("Failed to stop Service: " + self.name)
        self.status = StatusEnum.STOPPED
        self.initStarted = False

    def stopService(self):
        # implemented by child classes
        return True

    def getState(self):
        return self.state

class StatusEnum(Enum):
    NOTSTARTED = 0
    RUNNING = 1
    STOPPED = 2
    FAILED =3
