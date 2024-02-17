import asyncio
import threading

from .LedAnimation import LedAnimation
import typing

def readyFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=0, brightness=0)
    ledInterface.write()
    f.set_result(True)
    return f

ready = LedAnimation("ready", 1)
ready.setAnimation(readyFunc)

def wakeFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0.1)
    ledInterface.write()
    f.set_result(True)
    return f

wake = LedAnimation("wake", 1)
wake.setAnimation(wakeFunc)

def workingFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0.1)
    ledInterface.write()

    nextFrame = circle(ledInterface, 0, 1)

    async def circleFunc():
        await nextFrame()
        ledInterface.write()

    ledInterface.setInterval(circleFunc, 100)
    return f

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
                clear(ledInterface, 2000)
                f.set_result(True)

    ledInterface.setInterval(circleFunc, 100)
    return f

setup = LedAnimation("setup",1)
setup.setAnimation(setupFunc)

def successFunc(ledInterface, ledAnimation):
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
                clear(ledInterface, 2000)
                f.set_result(True)

    ledInterface.setInterval(circleFunc, 100)
    return f

success = LedAnimation("success", 1)
success.setAnimation(successFunc)

def failFunc(ledInterface, ledAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLed()
    i = 0
    ledInterface.setAll(color_r=255, color_g=0, color_b=0, brightness=0.2)
    ledInterface.write()
    clear(ledInterface,100)
    setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=200)
    clear(ledInterface,300)
    setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=400)
    clear(ledInterface,500)
    setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=600)
    clear(ledInterface,800)
    delay(f.set_result,900,True)

fail = LedAnimation("fail", 1)
fail.setAnimation(failFunc)

def notunderstoodFunc(ledInterface, ledAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLed()
    i = 0
    ledInterface.setAll(color_r=255, color_g=0, color_b=0, brightness=0.2)
    ledInterface.write()
    clear(ledInterface, 200)
    setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=400)
    clear(ledInterface, 600)
    setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=800)
    delay(f.set_result, 900, True)

notunderstood = LedAnimation("notunderstood", 1)
notunderstood.setAnimation(notunderstoodFunc)





def clear(ledInterface, delay):
    def func():
        print("clearing leds")
        ledInterface.clearAll()
        ledInterface.write()

    t = threading.Timer(delay/1000, func)
    t.start()

def setAll(ledInterface, color_r, color_g, color_b, brightness, delay):
    def func():
        ledInterface.setAll(color_r, color_g, color_b, brightness)
        ledInterface.write()

    t = threading.Timer(delay/1000, func)
    t.start()

def delay(func, delay, *args):
    t = threading.Timer(delay / 1000, func, args)
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




