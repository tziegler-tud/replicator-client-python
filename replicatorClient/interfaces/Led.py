import math


class Led:
    def __init__(self, ledInterface, id):
        self.ledInterface = ledInterface
        self.id = id
        self.color_r = 0
        self.color_g = 0
        self.color_b = 0

        self.state = False
        self.lastBrightness = 0.1
        self.brightness = 0
        self.buffer = bytearray([0xE0,0x00,0x00,0x00])

    def setColors(self, r=0, g=0, b=0):
        self.color_r = r
        self.color_g = g
        self.color_b = b
        self.writeColorsToBuffer()

    def setColor_r(self,v):
        self.color_r = v
        self.writeColorsToBuffer()

    def setColor_g(self,v):
        self.color_g = v
        self.writeColorsToBuffer()

    def setColor_b(self,v):
        self.color_b = v
        self.writeColorsToBuffer()

    def writeColorsToBuffer(self):
        self.buffer[1] = self.color_b
        self.buffer[2] = self.color_g
        self.buffer[3] = self.color_r
        return self.buffer

    def on(self):
        if self.brightness == 0:
            self.setBrightness(self.lastBrightness)
        self.state = True

    def off(self):
        self.state = False
        self.brightness = 0
        self.lastBrightness = self.brightness
        self.setBrightnessRaw(0)

    def setBrightness(self, brightness):
        if brightness < 0: brightness = 0
        if brightness > 1: brightness = 1
        self.brightness = brightness

        self.buffer[0] = self.getBrightnessValue() | 0b11100000

    def setBrightnessRaw(self, brightness):
        self.buffer[0] = brightness | 0b11100000

    def writeToInterface(self):
        self.ledInterface.setBuffer(self.id, self.buffer)

    def getBrightnessValue(self):
        return math.ceil(self.brightness * 31)
