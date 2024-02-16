import asyncio
import threading

from .LedAnimation import LedAnimation
import typing

async def readyFunc(ledInterface, ledAnimation: LedAnimation):
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=0, brightness=0)
    ledInterface.write()

ready = LedAnimation("ready", 1)
ready.setAnimation(readyFunc)

async def wakeFunc(ledInterface, ledAnimation: LedAnimation):
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0.1)
    ledInterface.write()

wake = LedAnimation("wake", 1)
wake.setAnimation(wakeFunc)

async def workingFunc(ledInterface, ledAnimation: LedAnimation):
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0.1)
    ledInterface.write()

    nextFrame = circle(ledInterface, 0, 1)

    async def circleFunc():
        await nextFrame()
        ledInterface.write()

    ledInterface.setInterval(circleFunc, 100)

working = LedAnimation("working", 1)
working.setAnimation(workingFunc)


def setupFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    i = 0
    ledInterface.setAll(color_r=0, color_g=255, color_b=0, brightness=0)
    ledInterface.write()

    nextFrame = fillingCircle(ledInterface, 0, 0.1)

    def circleFunc():
        nonlocal i
        nonlocal f

        if i < ledInterface.ledAmount:
            nextFrame()
            i += 1
            ledInterface.write()
            if i == ledInterface.ledAmount:
                ledInterface.clearInterval()
                clear(ledInterface, 1000)
                f.set_result(True)

    ledInterface.setInterval(circleFunc, 1000)
    return f

setup = LedAnimation("setup",1)
setup.setAnimation(setupFunc)

def clear(ledInterface, delay):
    def func():
        ledInterface.setAll(color_r=0, color_g=0, color_b=0, brightness=0)
        ledInterface.write()

    t = threading.Timer(delay, func)
    t.start()
def circle(ledInterface, startBrighness: int, endBrightness: int):

    index = 0
    maxIndex = ledInterface.ledAmount -1
    leds = ledInterface.getLeds()
    range = endBrightness - startBrighness
    step = range / 2
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0)

    def left(index, amount):
        val = index - amount
        if val >= 0: return val
        else: return maxIndex - amount +1

    def nextFrame():
        nonlocal index
        index = (index + 1) % (maxIndex +1)
        leds[index].setBrightness(endBrightness)
        leds[(index+1) % (maxIndex + 1)].setBrightness(endBrightness - step)
        leds[left(index,1)].setBrightness(endBrightness - step)
        leds[left(index, 2)].setBrightness(startBrighness)

    return nextFrame

def fillingCircle(ledInterface, startBrightness: int, endBrightness: int):
    index = 0
    maxIndex = ledInterface.ledAmount - 1
    leds = ledInterface.getLeds()
    range = endBrightness - startBrightness
    step = range / 2
    def nextFrame():
        nonlocal index
        index = (index + 1) % (maxIndex +1)
        leds[index].setBrightness(endBrightness)

    return nextFrame




