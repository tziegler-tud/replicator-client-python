import asyncio

class Interface:
    def __init__(self):
        self.active = False
        self.interval = None
        self.name = "Interface"
    def initFunc(self):
        return True

    def debug(self, msg):
        print("<DEBUG>: " + self.name + ": "  + msg)

    def error(self, msg):
        print("<ERROR>: " + self.name + ": " + msg)

    def warn(self, msg):
        print("<WARNING>: " + self.name + ": " + msg)

    def to_json(self):
        return {"name": self.name, "active": self.active}

    async def handleEvent(self, event, **kwargs):
        if not self.active:
            self.error("Interface is inactive.")
        return self.handleEventInternal(event, **kwargs)

    async def handleEventInternal(self, event, **kwargs):
        if self.interval is not None:
            self.interval = None
        match event.value:
            # case "setupComplete":
            # case "ready":
            # case "wake":
            # case "understood":
            # case "working":
            # case "notUnderstood":
            # case "failed":
            # case "success":
            case _:
                self.warn("Unhandled event type.")
                return False

    def isActive(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
        if self.interval is not None:
            self.interval = None
