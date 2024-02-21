import asyncio
import logging
import threading
from enum import Enum

from .Service import Service
from .InterfaceService import InterfaceService
from replicatorClient.interfaces.Interface import InterfaceEvents

from .CommunicationService import CommunicationService


class VoiceCommandService(Service):

    instance = None

    tasks = set()

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
    async def processCommandAsync(command):
        interfaceService = InterfaceService.getInstance()
        result = None

        #
        if command.is_understood:
            communicationService = CommunicationService.getInstance()
            try:
                result = await communicationService.send_command(command)
            except Exception as err:
                print("Failed to send command: " + str(err))
                interfaceService.handleEvent(InterfaceEvents.CRITICALFAIL)
                return False
            else:
                if result.result == "success":
                    print("Command was successfully executed.")
                    print("Server executed intent: " + result.response["command"]["intent"])
                    interfaceService.handleEvent(InterfaceEvents.SUCCESS)
                    return result
                else:
                    res = result.response["result"]
                    reason = "Unknown error."
                    if res is not None:
                        reason = res.get("error", reason)
                    print("Command was rejected by server. Reason: " + str(reason))
                    interfaceService.handleEvent(InterfaceEvents.FAIL)
                    return result
        else:
            interfaceService.handleEvent(InterfaceEvents.NOTUNDERSTOOD)
            return False

    # @staticmethod
    # def processCommand(command):
    #     interfaceService = InterfaceService.getInstance()
    #     result = None
    #
    #     # def process_command(command, cb):
    #
    #     def cb(task):
    #         VoiceCommandService.tasks.discard(task)
    #         try:
    #             if result.result == "success":
    #                 print("Command was successfully executed.")
    #                 print("Server executed intent: " + result.response["command"]["intent"])
    #                 interfaceService.handleEvent(InterfaceEvents.SUCCESS)
    #                 return result
    #             else:
    #                 print("Command was rejected by server. Reason: " + str(result.error))
    #                 interfaceService.handleEvent(InterfaceEvents.FAIL)
    #                 return result
    #         except Exception as e:
    #             print("InterfaceService: Handling failed for interface.")
    #         finally:
    #             pass
    #     #
    #     if command.is_understood:
    #         communicationService = CommunicationService.getInstance()
    #     #     try:
    #     #         communicationService.send_command_callback(command, cb)
    #     #     except Exception as err:
    #     #         print("Failed to send command: " + str(err))
    #     #         return False
    #
    #         async def process_command(command):
    #             await communicationService.send_command(command)
    #
    #         def thread_runner(command):
    #             loop = asyncio.new_event_loop()
    #             # asyncio.set_event_loop(loop)
    #             task = loop.create_task(process_command(command))
    #             task.add_done_callback(cb)
    #             VoiceCommandService.tasks.add(task)
    #             loop.run_until_complete(task)
    #             loop.close()
    #
    #         try:
    #             # # run in different thread
    #             t = threading.Thread(target=thread_runner, args=[command])
    #             t.start()
    #             # thread_runner(command)
    #         except Exception as err:
    #             print("Failed to send command: " + str(err))
    #             return False

    #
    # else:
    #     interfaceService.handleEvent(InterfaceEvents.NOTUNDERSTOOD)
    #     return False

class Command:
    def __init__(self, is_understood=False, intent="", slots={}):
        self.is_understood = is_understood
        self.intent = intent
        self.slots = slots

    def to_json(self):
        return {
            "isUnderstood": self.is_understood,
            "intent": self.intent,
            "slots": self.slots
        }
