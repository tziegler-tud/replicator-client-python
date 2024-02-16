import fs
import logging
from localStoragePy import localStoragePy
import json
import os
from replicatorClient.definitions import CONFIG_DIR

class SettingsService:

    localStorage = localStoragePy('replicatorClient', 'json')
    configDir = CONFIG_DIR

    def __init__(self):
        self.initStarted = False
        self.debugLabel = "SettingsService: "
        self.name= "SettingsService"
        self.settings = None
        self.defaultSettings = {
            "system": {
                "debugLevel": 0,
                "enableGpio": False
            },
            "recording": {
                "porcupineSensitivity": 0.6,
                "rhinoSensitivity": 0.7,
                "endpointDurationSec": 0.6,
            }
        }

    def debug(self, message):
        logging.warning(self.debugLabel + message)

    def start(self, *args):
        self.initStarted = True
        self.initFunc(args)

    def initFunc(self, args):

        # read config files
        print("Initializing SettingsService...")

        self.interfaceConfig = None
        try:
            i = open(os.path.join(SettingsService.configDir, "interface.json"))
            self.interfaceConfig = json.load(i)
        except IOError:
            logging.warning("Failed to read interface.json from config directory. ")

        self.voiceConfig = None
        try:
            i = open(os.path.join(SettingsService.configDir, "picovoice.json"))
            self.voiceConfig = json.load(i)
        except IOError:
            logging.warning("Failed to read interface.json from config directory. ")

        try:
            result = self.load()
        except:
            result = self.create()
        else:
            self.settings = {
                "system": {
                    "debugLevel": result["system"]["debugLevel"] or self.defaultSettings["system"]["debugLevel"],
                    "enableGpio": result["system"]["enableGpio"] or self.defaultSettings["system"]["enableGpio"]
                },
                "recording": {
                    "porcupineSensitivity": result["recording"]["porcupineSensitivity"] or self.defaultSettings["recording"]["porcupineSensitivity"],
                    "rhinoSensitivity": result["recording"]["rhinoSensitivity"] or self.defaultSettings["recording"]["rhinoSensitivity"],
                    "endpointDurationSec": result["recording"]["endpointDurationSec"] or self.defaultSettings["recording"]["endpointDurationSec"]
                }
            }
        finally:
            return self.settings

    def getSettings(self):
        return self.settings

    def getInterfaceConfig(self):
        return self.interfaceConfig

    def getVoiceConfig(self):
        return self.voiceConfig

    def load(self):
        data = {
                "system": {
                    "debugLevel": self.getKey("debugLevel"),
                    "enableGpio": self.getKey("enableGpio")
                },
                "recording": {
                    "porcupineSensitivity": self.getKey("porcupineSensitivity"),
                    "rhinoSensitivity": self.getKey("rhinoSensitivity"),
                    "endpointDurationSec": self.getKey("endpointDurationSec"),
                },
                "identifier": self.getKey("identifier"),
                "version": self.getKey("version")
            }
        return data

    def create(self):
        for key in self.defaultSettings:
            self.localStorage.setItem(key, self.defaultSettings[key])


    def getKey(self, key):
        return self.localStorage.getItem(key)

    def setKey(self, key, value):
        return self.localStorage.setItem(key, value)

