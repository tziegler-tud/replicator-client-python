import asyncio
from threading import Timer
from subprocess import run, call
from fs import fs
import os
from replicatorClient.definitions import ROOT_DIR, DATA_DIR

from replicatorClient.interfaces.Interface import Interface
class SoundInterface(Interface):
    def __init__(self):
        super().__init__()
        self.soundDirPath = os.path.join(DATA_DIR, "sounds")
        self.errMsg = "SoundInterface Error: "

        self.sounds = {
            "SETUPCOMPLETE": "power_up1_clean.wav",
            "READY": "power_up1_clean.wav",
            "WAKE": "communications_start_transmission.wav",
            "FAIL": "fail.wav",
            "NOTUNDERSTOOD": "notunderstood.wav",
            "SUCCESS": "communications_end_transmission.wav"
        }

        self.files = {
            "SETUPCOMPLETE": fs.join(self.soundDirPath, self.sounds["SETUPCOMPLETE"]),
            "READY": fs.join(self.soundDirPath, self.sounds["READY"]),
            "WAKE": fs.join(self.soundDirPath, self.sounds["WAKE"]),
            "FAIL": fs.join(self.soundDirPath, self.sounds["FAIL"]),
            "NOTUNDERSTOOD": fs.join(self.soundDirPath, self.sounds["NOTUNDERSTOOD"]),
            "SUCCESS": fs.join(self.soundDirPath, self.sounds["SUCCESS"]),
        }

    def initFunc(self):
        self.active = True

    async def handleEvent(self, event, **kwargs):
        if not self.active:
            self.error("Interface is inactive.")
        return await self.handleEventInternal(event, **kwargs)

    async def handleEventInternal(self, event, **kwargs):
        if self.interval is not None:
            self.interval = None

        match event.value:
            case "setupComplete":
                return await self.play(self.files["SETUPCOMPLETE"])
            case "ready":
                return await self.play(self.files["READY"])
            case "wake":
                return await self.play(self.files["WAKE"])
            case "understood":
                # return self.play(self.files["UNDERSTOOD"])
                pass
            case "working":
                # return self.play(self.files["WORKING"])
                pass
            case "notUnderstood":
                return await self.play(self.files["NOTUNDERSTOOD"])
            case "failed":
                return await self.play(self.files["FAIL"])
            case "success":
                return await self.play(self.files["SUCCESS"])
            case _:
                self.warn("Unhandled event type.")
                return Exception("Unhandled event type.")

        return True

    async def play(self, path, duration=None, delay=None):
        args = ""
        if duration is not None:
            args += "--duration=" + str(duration)
        if delay is not None:
            t = Timer(1.0, self.playInternal, args=(path, args))
            t.start()
        else:
            self.playInternal(path, args)

    def playInternal(self, path, args=""):
        # run(["aplay", args, path])
        cmd = 'aplay'
        result = run([cmd, path], capture_output=True, text=True)
        print(result)