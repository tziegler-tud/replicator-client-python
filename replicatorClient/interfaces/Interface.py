import asyncio

class Interface:
    def __init__(self):
        self.active = False
        self.interval = None

    def initFunc(self):
        future = asyncio.Future()
        future.set_result("Interface initialized")

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

    def isActive(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
        if self.interval is not None:
            self.interval = None
