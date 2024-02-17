import asyncio

from replicatorClient.services.SettingsService import SettingsService
from replicatorClient.services.InterfaceService import InterfaceService, events as InterfaceEvents
from flask import Flask

from quart import Quart, render_template, websocket

from replicatorClient.services.VoiceCommandService import VoiceCommandService
from replicatorClient.services.VoiceRecognitionService import VoiceRecognitionService


async def background_service(app):

    settingsService = SettingsService()
    settingsService.start()

    print(settingsService.getSettings())

    interfaceService = InterfaceService()
    interfaceService.start()

    voiceCommandService = VoiceCommandService()
    voiceCommandService.start()

    voiceRecognitionService = VoiceRecognitionService()
    voiceRecognitionService.start()


    interfaceService.handleEvent(InterfaceEvents.SETUPCOMPLETE)


    @app.route("/test/interface/<event>")
    async def interfaceTest(event):
        match event:
            case "setupComplete":
                interfaceService.handleEvent(InterfaceEvents.SETUPCOMPLETE)
            case "ready":
                interfaceService.handleEvent(InterfaceEvents.READY)
            case "wake":
                interfaceService.handleEvent(InterfaceEvents.WAKE)
                # case "understood":
                interfaceService.handleEvent(InterfaceEvents.UNDERSTOOD)
            case "working":
                interfaceService.handleEvent(InterfaceEvents.WORKING)
            case "notunderstood":
                interfaceService.handleEvent(InterfaceEvents.NOTUNDERSTOOD)
            case "failed":
                interfaceService.handleEvent(InterfaceEvents.FAILED)
            case "success":
                interfaceService.handleEvent(InterfaceEvents.SUCCESS)
            case _:
                return "<p>Unexpected event type.</p>"

        print("interface test finished!")
        return "<p>Playing event: " + event + "</p>"


app = Quart(__name__)
asyncio.run(background_service(app))
app.run()


