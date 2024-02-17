import asyncio
import logging
from enum import Enum

from .Service import Service
from .InterfaceService import InterfaceService, events as InterfaceEvents


class VoiceCommandService(Service):

    instance = None

    @staticmethod
    def getInstance():
        if VoiceCommandService.instance is not None:
            return VoiceCommandService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if VoiceCommandService.instance is not None:
            return VoiceCommandService.instance
        else:
            VoiceCommandService.instance = VoiceCommandService()
    def __init__(self):
        super().__init__()
        self.name = "VoiceCommandService"
        VoiceCommandService.instance = self

    @staticmethod
    def processKeyword(self):
        interfaceService = InterfaceService.getInstance()
        interfaceService.handleEvent(InterfaceEvents.WAKE)

    @staticmethod
    def processCommand(command):
        interfaceService = InterfaceService.getInstance()

        print(command)
        if command.is_understood:
            interfaceService.handleEvent(InterfaceEvents.SUCCESS)
