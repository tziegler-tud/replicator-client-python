import asyncio
import nest_asyncio
nest_asyncio.apply()

from replicatorClient.services.CommunicationService import CommunicationService
from replicatorClient.services.SettingsService import SettingsService
from replicatorClient.services.InterfaceService import InterfaceService
from replicatorClient.interfaces.Interface import InterfaceEvents
from flask import Flask

from quart import Quart, request, jsonify, abort, render_template, websocket

from replicatorClient.services.VoiceCommandService import VoiceCommandService, Command
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
    voiceRecognitionService.start(main_loop)

    communicationService = CommunicationService()
    await communicationService.start()

    interfaceService.handleEvent(InterfaceEvents.SETUPCOMPLETE)

    # await VoiceCommandService.processCommandAsync(Command(True, "FailOnPurpose", {}))

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
            case "fail":
                interfaceService.handleEvent(InterfaceEvents.FAIL)
            case "success":
                interfaceService.handleEvent(InterfaceEvents.SUCCESS)
            case _:
                return "<p>Unexpected event type.</p>"

        print("interface test finished!")
        return "<p>Playing event: " + event + "</p>"


    @app.get("/test/communication/send")
    async def send_command():
        main_loop.run_until_complete(VoiceCommandService.processCommandAsync(Command(True, "Ignore", {})))
        # await VoiceCommandService.processCommandAsync(Command(True, "Ignore", {}))
        return jsonify({"status": "success"})

    @app.get("/api/v1/")
    async def get_client_information():
        pass
    @app.post("/api/v1/requestAuthentication")
    async def connectToServer():
        data = await request.get_json()
        result = await communicationService.handle_tcp_connection_request(data)
        return {"clientId": result["server"]["clientId"], "connected": result["state"]}

    @app.get("/api/v1/settings")
    async def get_settings():
        return jsonify(settingsService.getSettings())

    @app.post("/api/v1/settings")
    async def update_settings():
        data = await request.get_json()
        result = settingsService.setKey(data["key"], data["value"])
        if result is not None:
            return jsonify(result)
        else:
            abort(401)

    @app.post("/api/v1/tcpTest")
    async def tcp_test():
        data = await request.get_json()
        result = await communicationService.handle_tcp_connection_request(data)
        return jsonify(result)


app = Quart(__name__)
main_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_loop)
asyncio.run(background_service(app))
app.run(host="0.0.0.0", port=5000)


