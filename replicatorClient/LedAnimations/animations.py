import asyncio
import threading

from .LedAnimation import LedAnimation
import typing

def _readyFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=0, brightness=0)
    ledInterface.write()
    f.set_result(True)
    return f

ready = LedAnimation("ready", 1)
ready.setAnimation(_readyFunc)

def _wakeFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0.1)
    ledInterface.write()
    f.set_result(True)
    return f

wake = LedAnimation("wake", 1)
wake.setAnimation(_wakeFunc)

def _workingFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    ledInterface.setAll(color_r=0, color_g=0, color_b=255, brightness=0.1)
    ledInterface.write()

    nextFrame = __circle(ledInterface, 0, 1)

    async def circleFunc():
        await nextFrame()
        ledInterface.write()

    ledInterface.setInterval(circleFunc, 100)
    return f

working = LedAnimation("working", 1)
working.setAnimation(_workingFunc)


def _setupFunc(ledInterface, ledAnimation: LedAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    i = 0
    ledInterface.setAll(color_r=0, color_g=255, color_b=0, brightness=0)
    ledInterface.write()

    nextFrame = __fillingCircle(ledInterface, 0, 0.1)

    def circleFunc():
        nonlocal i
        nonlocal f

        if i < ledInterface.ledAmount:
            nextFrame()
            i += 1
            ledInterface.write()
            if i == ledInterface.ledAmount:
                ledInterface.clearInterval()
                __clear(ledInterface, 2000)
                f.set_result(True)

    ledInterface.setInterval(circleFunc, 100)
    return f

setup = LedAnimation("setup",1)
setup.setAnimation(_setupFunc)

def _successFunc(ledInterface, ledAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    i = 0
    ledInterface.setAll(color_r=0, color_g=255, color_b=0, brightness=0)
    ledInterface.write()

    __clear(ledInterface, 2000)
    __delay(f.set_result,2200,True)

    # nextFrame = __fillingCircle(ledInterface, 0, 0.1)
    #
    # def circleFunc():
    #     nonlocal i
    #     nonlocal f
    #
    #     if i < ledInterface.ledAmount:
    #         nextFrame()
    #         i += 1
    #         ledInterface.write()
    #         if i == ledInterface.ledAmount:
    #             ledInterface.clearInterval()
    #
    #             f.set_result(True)
    #
    # ledInterface.setInterval(circleFunc, 100)
    return f

success = LedAnimation("success", 1)
success.setAnimation(_successFunc)

def _failFunc(ledInterface, ledAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    i = 0
    ledInterface.setAll(color_r=255, color_g=0, color_b=0, brightness=0.2)
    ledInterface.write()
    __clear(ledInterface,100)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=200)
    __clear(ledInterface,300)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=400)
    __clear(ledInterface,500)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=600)
    __clear(ledInterface,800)
    __delay(f.set_result,900,True)

fail = LedAnimation("fail", 1)
fail.setAnimation(_failFunc)

def _criticalFailFunc(ledInterface, ledAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    i = 0
    ledInterface.setAll(color_r=255, color_g=0, color_b=0, brightness=0.2)
    ledInterface.write()
    __clear(ledInterface,100)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=200)
    __clear(ledInterface,300)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=400)
    __clear(ledInterface,500)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=600)
    __clear(ledInterface,800)
    __delay(f.set_result,900,True)

criticalFail = LedAnimation("fail", 1)
criticalFail.setAnimation(_criticalFailFunc)


def _notunderstoodFunc(ledInterface, ledAnimation):
    f = asyncio.Future()
    leds = ledInterface.getLeds()
    i = 0
    ledInterface.setAll(color_r=255, color_g=0, color_b=0, brightness=0.2)
    ledInterface.write()
    __clear(ledInterface, 200)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=400)
    __clear(ledInterface, 600)
    __setAll(ledInterface, color_r=255, color_g=0, color_b=0, brightness=0.2, delay=800)
    __clear(ledInterface, 1000)
    __delay(f.set_result, 1000, True)

notunderstood = LedAnimation("notunderstood", 1)
notunderstood.setAnimation(_notunderstoodFunc)





def __clear(ledInterface, delay):
    def func():
        print("clearing leds")
        ledInterface.clearAll()
        ledInterface.write()

    t = threading.Timer(delay/1000, func)
    t.start()

def __setAll(ledInterface, color_r, color_g, color_b, brightness, delay):
    def func():
        ledInterface.setAll(color_r=color_r, color_g=color_g, color_b=color_b, brightness=brightness)
        ledInterface.write()

    t = threading.Timer(delay/1000, func)
    t.start()

def __delay(func, delay, *args):
    t = threading.Timer(delay / 1000, func, args)
    t.start()


def __circle(ledInterface, startBrighness: int, endBrightness: int):

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

def __fillingCircle(ledInterface, startBrightness: int, endBrightness: int):
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




