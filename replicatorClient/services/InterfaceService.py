import asyncio
import logging
from enum import Enum

from .Service import Service

from replicatorClient.interfaces.LedInterface import LedInterface
from replicatorClient.interfaces.SoundInterface import SoundInterface
from ..interfaces.MockLedInterface import MockLedInterface


class InterfaceService(Service):
    instance = None

    @staticmethod
    def getInstance():
        if InterfaceService.instance is not None:
            return InterfaceService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if InterfaceService.instance is not None:
            return InterfaceService.instance
        else:
            InterfaceService.instance = InterfaceService()

    def __init__(self):
        super().__init__()
        self.name = "InterfaceService"
        self.interfaces = []
        self.ledInterface = None
        self.soundInterface = None

        self.interfaceConfig = self.settingsService.getInterfaceConfig()

        InterfaceService.instance = self

    def initFunc(self, *args):
        print("Initializing InterfaceService...")
        errMsg = "Failed to initialize InterfaceService. "

        interfaces = self.interfaceConfig["interfaces"]
        if not interfaces:
            self.debug(errMsg + "Invalid configuration.")

        for interfaceConfig in interfaces:
            self.loadInterfaceFromConfig(interfaceConfig)

    def loadInterfaceFromConfig(self, interfaceConfig):
        errMsg = "Failed to load interface: "
        if type(interfaceConfig) is str:
          interfaceConfig = {
              "type": interfaceConfig,
              "constructorArgs": {}
          }
        itype = interfaceConfig["type"]
        if itype is None:
          self.debug(errMsg)
          return False

        if self.getInterfaceByType(itype):
            self.debug("Warning: Interface of type '{}' already exists.".format(itype))
            return False
        try:
            match itype:
                case types.LED.value:
                    self.addLedInterface(interfaceConfig["constructorArgs"])
                case types.SOUND.value:
                    self.addSoundInterface(interfaceConfig["constructorArgs"])
                case types.DISPLAY.value, types.GENERIC:
                    self.debug(errMsg + "Interface of type '{}' not supported by current version.".format(itype))
                    # self.addGenericInterface(interfaceConfig.constructorArgs)
                    pass
                case _:
                    self.debug(errMsg + "Unknown Interface type '{}'".format(itype))
        except:
            logging.warning("Failed to create Interface for type '{}'.".format(itype))
        else:
            self.debug("Interface for type '{}' created successfully.".format(itype))

    def addLedInterface(self, interfaceArgs):
        type = types.LED
        if "ledAmount" not in interfaceArgs: interfaceArgs["ledAmount"] = 1
        if "clockDivider" not in interfaceArgs: interfaceArgs["clockDivider"] = 128
        if "mock" not in interfaceArgs: interfaceArgs["mock"] = False

        if interfaceArgs["mock"]:
            ledInterface = MockLedInterface(ledAmount=interfaceArgs["ledAmount"], clockDivider=interfaceArgs["clockDivider"])
        else:
            ledInterface = LedInterface(ledAmount=interfaceArgs["ledAmount"], clockDivider=interfaceArgs["clockDivider"])
        ledInterface.initFunc()
        self.interfaces.append(savedInterface(type, ledInterface))

    def addSoundInterface(self, interfaceArgs):
        type = types.SOUND
        soundInterface = SoundInterface()
        soundInterface.initFunc()
        self.interfaces.append(savedInterface(type, soundInterface))


    # def addDisplayInterface(self, interfaceArgs):
    #     type = types.DISPLAY
    #     displayInterface = DisplayInterface(interfaceArgs)
    #     displayInterface.initFunc()
    #
    # def addGenericInterface(self, interfaceArgs):
    #     type = types.GENERIC
    #     genericInterface = GenericInterface(interfaceArgs)
    #     genericInterface.initFunc()

    def handleEvent(self, interfaceEvent, interfaceFilter=[], interfaceFilterType= "include"):

        tasks = set()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        interfaces = self.filterInterfaces(interfaceFilter, interfaceFilterType)

        def cb(task):
            try:
                result = task.result()
                print("task finished!")
            except Exception as e:
                print("InterfaceService: Handling failed for interface.")
            finally:
                tasks.discard(task)

        for i in interfaces:
            if i.interface.isActive():
                t = loop.create_task(i.interface.handleEventInternal(interfaceEvent))
                tasks.add(t)
                t.add_done_callback(cb)
        return True

    def filterInterfaces(self, interfaceFilter = [], interfaceFilterType = "include"):
        filter = interfaceFilter
        if type(interfaceFilter) is str:
            filter = [interfaceFilter]

        match interfaceFilterType:
            case "include":
                if len(filter) == 0:
                    return self.interfaces
                else:
                    return [interface for interface in self.interfaces if interface.type in interfaceFilter]
            case "exclude":
                if len(filter) == 0:
                    return []
                else:
                    return [interface for interface in self.interfaces if interface.type not in interfaceFilter]


    def getInterfaceByType(self, type):
        for item in self.interfaces:
            if item.type.value == type: return item
        return None

    def getAll(self):
        return self.interfaces



class savedInterface:
    def __init__(self, type, interface):
        self.type = type
        self.interface = interface

class events(Enum):
    SETUPCOMPLETE = "setupComplete"
    READY = "ready"
    WAKE = "wake"
    UNDERSTOOD = "understood"
    WORKING = "working"
    NOTUNDERSTOOD = "notUnderstood"
    FAILED = "failed"
    SUCCESS = "success"

class types(Enum):
    LED = "LedInterface"
    SOUND = "SoundInterface"
    DISPLAY = "DisplayInterface"
    GENERIC = "GenericInterface"
