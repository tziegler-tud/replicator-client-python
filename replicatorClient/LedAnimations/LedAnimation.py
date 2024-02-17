import asyncio


class LedAnimation:
    def __init__(self, title, minAmount):
        self.title = title
        self.minAmount = minAmount
        def animation():
            return True
        self.animation = animation
        self.active = False

    async def play(self,ledInterface):
        self.active = True
        self.animation(ledInterface, self)

    def stop(self, ledInterface):
        self.active = False
        ledInterface.clearAll()

    def setAnimation(self, func):
        self.animation = func


