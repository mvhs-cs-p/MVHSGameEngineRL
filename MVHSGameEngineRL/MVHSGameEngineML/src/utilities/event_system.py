
from MVHSGameEngineML.src.utilities.logger import Logger


class EventSystem:
    def __init__(self):
        self.events = {}

    def subscribe(self, event_name, callback):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    def unsubscribe(self, event_name, callback):
        if event_name not in self.events:
            return
        if callback in self.events[event_name]:
            self.events[event_name].remove(callback)

    def broadcast(self, event_name, **kwargs):
        if event_name not in self.events:
            return
        for callback in self.events[event_name]:
            callback(**kwargs)
