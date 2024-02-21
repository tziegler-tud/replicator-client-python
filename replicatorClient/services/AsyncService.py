import asyncio
import logging
from enum import Enum
from .SettingsService import SettingsService



class AsyncService:
    instance = None

    @staticmethod
    def getInstance():
        if AsyncService.instance is not None:
            return AsyncService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if AsyncService.instance is not None:
            return AsyncService.instance
        else:
            AsyncService.instance = AsyncService()

    def __init__(self):
        self.name = "unidentified Service"
        self.status = StatusEnum.NOTSTARTED

        self.init = asyncio.Future()

        self.systemSettings = None
        self.debugLabel = "Service: "
        self.enableDebug = True

        self.settingsService = SettingsService.getInstance()
        AsyncService.instance = self

    def debug(self, message, level = 0):
        if self.settingsService.getSettings()["system_debugLevel"] <= level: print(self.debugLabel + message)

    async def initFunc(self, *args):
        return True

    async def start(self, *args):
        self.debug("Starting Service: " + self.name)
        if self.status == StatusEnum.RUNNING:
            return True
        self.initStarted = True
        self.systemSettings = self.settingsService.getSettings()
        try:
            self.status = StatusEnum.RUNNING
            await self.initFunc(args)
            return True
        except Exception as e:
            self.status = StatusEnum.FAILED
            self.debug("ERROR: Service startup failed: " + self.name)
            logging.error("ERROR: Service failed to start: "+ self.name)
            return False

class StatusEnum(Enum):
    NOTSTARTED = 0
    RUNNING = 1
    STOPPED = 2
    FAILED =3
