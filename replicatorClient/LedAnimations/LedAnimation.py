import asyncio


class LedAnimation:
    def __init__(self, title, minAmount):
        self.title = title
        self.minAmount = minAmount
        def animation():
            return True
        self.animation = animation
        self.active = False

    def play(self,ledInterface):
        future = asyncio.Future()
        self.active = True
        f = self.animation(ledInterface, self)
        f.add_done_callback(lambda: future.set_result(True))
        return future

    def stop(self, ledInterface):
        self.active = False
        ledInterface.clearAll()

    def setAnimation(self, func):
        self.animation = func


