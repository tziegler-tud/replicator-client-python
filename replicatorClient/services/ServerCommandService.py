import asyncio
import logging
import threading
from enum import Enum

from .Service import Service
from .InterfaceService import InterfaceService, InterfaceTypes
from ..helpers.TcpResponseGenerator import tcp_response_generator


class ServerCommandService(Service):

    instance = None

    tasks = set()

    @staticmethod
    def getInstance():
        if ServerCommandService.instance is not None:
            return ServerCommandService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if ServerCommandService.instance is not None:
            return ServerCommandService.instance
        else:
            ServerCommandService.instance = ServerCommandService()
    def __init__(self):
        super().__init__()
        self.name = "ServerCommandService"
        ServerCommandService.instance = self

    @staticmethod
    def processCommand(data):
        ifs = InterfaceService.getInstance()
        command = data.get('command', "")
        args = data.get('args', {})
        try:
            match command:
                case Commands.INTERFACES.value.SOUND.value.DISABLE.value:
                    ifs.disableInterface(InterfaceTypes.SOUND.value)
                case Commands.INTERFACES.value.SOUND.value.ENABLE.value:
                    ifs.enableInterface(InterfaceTypes.SOUND.value)
                case Commands.INTERFACES.value.LED.value.DISABLE.value:
                    ifs.disableInterface(InterfaceTypes.LED.value)
                case Commands.INTERFACES.value.LED.value.ENABLE.value:
                    ifs.disableInterface(InterfaceTypes.LED.value)
                case Commands.INTERFACES.value.DISPLAY.value.DISABLE.value:
                    ifs.disableInterface(InterfaceTypes.DISPLAY.value)
                case Commands.INTERFACES.value.DISPLAY.value.ENABLE.value:
                    ifs.disableInterface(InterfaceTypes.DISPLAY.value)
        except:
            return tcp_response_generator.tpcResponse["COMMAND"]["INTERNAL_ERROR"]

        else:
            return tcp_response_generator.tpcResponse["COMMAND"]["SUCCESSFUL"]


class AudioInterfaceEnum(Enum):
    DISABLE = "disableAudio"
    ENABLE = "enableAudio"

class LedInterfaceEnum(Enum):
    DISABLE = "disableLed"
    ENABLE = "enableLed"
class DisplayInterfaceEnum(Enum):
    DISABLE = "disableDisplay"
    ENABLE = "enableDisplay"
class InterfaceEnum(Enum):
    SOUND = AudioInterfaceEnum
    LED = LedInterfaceEnum
    DISPLAY = DisplayInterfaceEnum
class Commands(Enum):
    INTERFACES = InterfaceEnum

