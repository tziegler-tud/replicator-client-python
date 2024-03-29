import asyncio
import threading

import spidev
import typing

from replicatorClient.LedAnimations.animations import ready, wake, working, setup, success, fail, criticalFail, notunderstood
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

from replicatorClient.interfaces.Interface import Interface, InterfaceEvents
from .Led import Led


class LedInterface(Interface):
    def __init__(self, ledAmount=1, clockDivider=128, enableDebug=False):
        super().__init__()
        self.ledAmount = ledAmount
        self.clockDivider = clockDivider
        self.leds = []
        self.enableDebug = enableDebug

        self.LED_START = 0b11100000

    def initFunc(self):

        for i in range(self.ledAmount):
            self.leds.append(Led(self, i))

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        ledBufferLength = self.ledAmount * 4
        self.ledBuffer = bytearray([0xE0, 0x00, 0x00, 0x00] * self.ledAmount)
        self.bufferLength = 4 + ledBufferLength + 4

        self.startFrame = bytearray([0x00] * 4)
        self.endFrame = bytearray([0xFF] * 4)

        self.ledBuffer = self.generateLedBuffer()
        self.writeBuffer = self.generateWriteBuffer()

        # set GPIO5 to HIGH
        GPIO.setup(29, GPIO.OUT)
        GPIO.output(29, GPIO.HIGH)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 1)
        self.clearAll()

        self.active = True

    def close(self):
        self.spi.close()

    def write(self):
        writeBuffer = self.generateWriteBuffer()
        if self.enableDebug: self.debug("Transfering buffer to spi. Content: " + str(writeBuffer))
        self.spi.xfer3(writeBuffer)

    def generateLedBuffer(self):
        ledBufferArray = []
        self.ledBuffer = bytearray()
        for led in self.leds:
            self.ledBuffer += led.buffer
        return self.ledBuffer

    def generateWriteBuffer(self):
        ledBuffer = self.generateLedBuffer()
        writeBuffer = self.startFrame + ledBuffer + self.endFrame
        return writeBuffer

    def setBuffer(self, ledIndex, buffer):
        pos = 4 + ledIndex * 4
        self.writeBuffer[pos] = buffer[0]
        self.writeBuffer[pos + 1] = buffer[1]
        self.writeBuffer[pos + 2] = buffer[2]
        self.writeBuffer[pos + 3] = buffer[3]

    def setAll(self, **kwargs):
        r = kwargs.get("color_r", 0)
        g = kwargs.get("color_g", 0)
        b = kwargs.get("color_b", 0)

        for led in self.leds:
            led.setColors(r,g,b)
            led.setBrightness(kwargs.get("brightness",0))

    def clearAll(self):
        for led in self.leds:
            led.off()
            led.setColors(0,0,0)
            led.setBrightness(0)

    def getLeds(self):
        return self.leds

    async def handleEventInternal(self, event, **kwargs):
        if self.interval is not None:
            self.interval = None

        match event:
            case InterfaceEvents.SETUPCOMPLETE:
                return await setup.play(self)
            case InterfaceEvents.READY:
                return await ready.play(self)
            case InterfaceEvents.WAKE:
                return await wake.play(self)
            # case "understood":
            #     return
            # case "working":
            case InterfaceEvents.NOTUNDERSTOOD:
                return await notunderstood.play(self)
            case InterfaceEvents.FAIL:
                return await fail.play(self)
            case InterfaceEvents.CRITICALFAIL:
                return await criticalFail.play(self)
            case InterfaceEvents.SUCCESS:
                return await success.play(self)
            case _:
                self.warn("Unhandled event type.")
                return Exception("Unhandled event type.")

        return True

    def setInterval(self, func, ms):
        self.interval = self.set_intervalSync(func, ms / 1000)
        return

    def clearInterval(self):
        if self.interval is not None:
            self.interval.cancel()
        self.interval = None

    def set_intervalAsync(self, func, sec):
        async def func_wrapper():
            await func()
            self.interval = self.set_intervalAsync(func, sec)

        t = Timer(sec, func_wrapper)
        return t

    def set_intervalSync(self, func, sec):
        def func_wrapper():
            func()
            self.interval = self.set_intervalSync(func, sec)

        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()