from replicatorClient.services.SettingsService import SettingsService
from replicatorClient.services.InterfaceService import InterfaceService, events as InterfaceEvents
from flask import Flask

app = Flask(__name__)

settingsService = SettingsService()
settingsService.start()

print(settingsService.getSettings())

interfaceService = InterfaceService(settingsService)
interfaceService.start()

interfaceService.handleEvent(InterfaceEvents.SETUPCOMPLETE)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"