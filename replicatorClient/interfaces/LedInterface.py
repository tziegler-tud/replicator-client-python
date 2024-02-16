import asyncio
import spidev
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

from replicatorClient.interfaces.Interface import Interface
from .Led import Led
class LedInterface(Interface):
    def __init__(self, ledAmount=1, clockDivider=128):
        super().__init__()
        self.ledAmount = ledAmount
        self.clockDivider = clockDivider
        self.leds = []

        self.LED_START = 0b11100000

    def initFunc(self):

        for i in range(self.ledAmount):
            self.leds.append(Led(self,i))

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        ledBufferLength = self.ledAmount * 4
        self.ledBuffer = bytearray([0xE0, 0x00,0x00,0x00] * self.ledAmount)
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

    def close(self):
        self.spi.close()

    def write(self):
        writeBuffer = self.generateWriteBuffer()
        self.spi.xfer(writeBuffer)

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

    def setAll(self, args):
        for led in self.leds:
            if args.color: led.setColor(args.color)
            if args.brightness: led.setBrightness(args.brightness)

    def clearAll(self):
        for led in self.leds:
            led.off()

    def getLeds(self):
        return self.leds

    def handleEvent(self, event, args):
        future = asyncio.Future()
        if not self.active:
            future.set_exception("Interface inactive.")
        if self.interval is not None:
            self.interval = None

        match event.value:
            # case "setupComplete":
            # case "ready":
            # case "wake":
            # case "understood":
            # case "working":
            # case "notunderstood":
            # case "failed":
            # case "success":
            case _:
                future.set_exception("Unhandled event type.")

        return future