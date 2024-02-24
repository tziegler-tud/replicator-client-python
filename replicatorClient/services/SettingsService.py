import time

import fs
import logging
import json
import os
from replicatorClient.definitions import CONFIG_DIR, STORAGE_DIR, RELEASE_VERSION

class SettingsService:

    instance = None
    configDir = CONFIG_DIR
    storageDir = STORAGE_DIR
    version = RELEASE_VERSION

    @staticmethod
    def getInstance():
        if SettingsService.instance is not None:
            return SettingsService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if SettingsService.instance is not None:
            return SettingsService.instance
        else:
            SettingsService.instance = SettingsService()

    def __init__(self):
        self.initStarted = False
        self.debugLabel = "SettingsService: "
        self.name= "SettingsService"
        self.settings = None
        self.default_settings = {
            "system_debugLevel": 0,
            "system_enableGpio": False,

            "recording_porcupineSensitivity": 0.6,
            "recording_rhinoSensitivity": 0.7,
            "recording_endpointDurationSec": 0.6,

            "identifier": "Replicator-Client-" + str(time.time()),
            "version": RELEASE_VERSION
        }
        SettingsService.instance = self

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
            i = open(os.path.join(SettingsService.configDir, "systemSettings.json"))
            self.systemConfig = json.load(i)
        except IOError:
            logging.warning("Failed to read systemSettings.json from config directory. ")

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

        self.settings = self.load()
        if self.settings is None:
            self.settings = self.create()

        return self.settings

    def create(self, params=None):
        defaults = self.default_settings
        if params is None:
            params = {}
        params = {**defaults, **params}
        self.settings = params
        return self.save()

    def getSettings(self):
        return self.settings

    def getSettings_server_format(self):
        return {
            "system": {
                "debugLevel": self.settings["system_debugLevel"],
                "enableGpio": self.settings["system_enableGpio"],
            },
            "recording": {
                "porcupineSensitivity": self.settings["recording_porcupineSensitivity"],
                "rhinoSensitivity": self.settings["recording_rhinoSensitivity"],
                "endpointDurationSec": self.settings["recording_endpointDurationSec"]
            },
            "identifier": self.settings["identifier"],
            "version": self.settings["version"]
        }

    def getInterfaceConfig(self):
        return self.interfaceConfig

    def getVoiceConfig(self):
        return self.voiceConfig

    def getKey(self, key):
        return self.settings[key]
    def setKey(self, key, value):
        self.settings[key] = value
        self.save()

    def getKey_server_format(self, key, data, category=""):
        # key is either "recording" "system"
        internalKey = self.server_key_to_internal_key(category, key)
        return self.settings[internalKey]

    def setKey_server_format(self, key, data, category=""):
        # key is either "recording" "system"
        internalKey = self.server_key_to_internal_key(category, key)
        self.settings[internalKey] = data
        self.save()

    # Server uses nested json keys: ["recording"]["endpointDurationSec"]
    def server_key_to_internal_key(self, categoryKey, innerKey):
        internalKey = ""
        if len(categoryKey) == 0:
            match innerKey:
                case "version":
                    internalKey = "version"
                case "identifier":
                    internalKey = "identifier"

        elif categoryKey == "recording":
            match innerKey:
                case "porcupineSensitivity":
                    internalKey = "recording_porcupineSensitivity"
                case "rhinoSensitivity":
                    internalKey = "recording_rhinoSensitivity"
                case "endpointDurationSec":
                    internalKey = "recording_endpointDurationSec"

        elif categoryKey == "system":
            match innerKey:
                case "debugLevel":
                    internalKey = "system_debugLevel"
        return internalKey


    def save(self):
        try:
            content = json.dumps(self.settings)
            # Check if systemStore dir exists
            store_path = SettingsService.storageDir
            file_path = os.path.join(SettingsService.storageDir, 'systemSettings.json')

            if not os.path.exists(store_path):
                os.makedirs(store_path)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            return self.settings  # Return a value indicating success if needed
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False  # Return a value indicating failure if needed

    def load(self):
        try:
            store_path = SettingsService.storageDir
            file_path = os.path.join(store_path, 'systemSettings.json')

            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                obj = json.loads(data)

            return self.loadWithDefaults(obj)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return None  # Return a value indicating failure if needed

    def loadWithDefaults(self, params):
        result = {**self.default_settings, **params}
        return result

    def loadServer(self):
        try:
            file_path = os.path.join(SettingsService.storageDir, 'server.json')

            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                obj = json.loads(data)

            return obj
        except Exception as e:
            print(f"Error loading settings: {e}")
            return None  # Return a value indicating failure if needed
    def saveServer(self, server):
        try:
            content = json.dumps(server.to_json())
            # Check if systemStore dir exists
            store_path = SettingsService.storageDir
            file_path = os.path.join(store_path, 'server.json')

            if not os.path.exists(store_path):
                os.makedirs(store_path)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            return True  # Return a value indicating success if needed
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False  # Return a value indicating failure if needed

