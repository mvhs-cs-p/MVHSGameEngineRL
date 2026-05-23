
from MVHSGameEngineML.src.utilities.logger import Logger
from MVHSGameEngineML.src.input.mouse_input_type import MouseInputType
from MVHSGameEngineML.src.input.key_input_type import KeyInputType




class PlayerInputManager:
    def __init__(self):
        self.wants_to_quit = False
        self._registered_mouse_down_events = {}
        self._registered_mouse_up_events = {}
        self._registered_mouse_up_events = {}
        self._registered_key_down_events = {}
        self._registered_key_up_events = {}
        self._registered_key_held_events = {}

    def register_key_input(self, input_type: KeyInputType, key: int, callback_method) -> None:
        if input_type == KeyInputType.KEY_DOWN:
            self.register_key_down(key, callback_method)





    def register_key_down(self, key: int, callback_method) -> None:

        """
        Register a call_back method with a key down event.
        :param key: key code, use pygame.k_...
        :param call_back: method that will be called when a pygame.KEYDOWN event is triggered by key.
        """

        if key in self._registered_key_down_events:
            Logger.log_error(self, f"Key: {key} already registered in key down events. Will be reregistered.")

        self._registered_key_down_events[key] = callback_method


    def register_key_up(self, key: int, call_back) -> None:

        """
        Register a call_back method with a key up event.
        :param key: key code, use pygame.k_...
        :param call_back: method that will be called when a pygame.KEYUP event is triggered by key.
        """

        if key in self._registered_key_up_events:
            Logger.log_error(self, f"Key: {key} already registered in key up events. Will be reregistered.")

        self._registered_key_up_events[key] = call_back


    def register_key_held(self, key, call_back):

        """
        Register a call_back method with a key held event.
        :param key: key code, use pygame.k_...
        :param call_back: method that will be called when pygame.key.get_pressed() is true for key.
        """

        if key in self._registered_key_held_events:
            Logger.log_error(self, f"Key: {key} already registered in key held events. Will be reregistered.")

        self._registered_key_held_events[key] = call_back


    def process_input(self, pygame, events):

        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down_event(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up_event(event)

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_motion_event(event)

            elif event.type == pygame.KEYDOWN:
                call_back = self._registered_key_down_events.get(event.key, None)
                if call_back is not None:
                    call_back()

            elif event.type == pygame.KEYUP:
                call_back = self._registered_key_up_events.get(event.key, None)
                if call_back is not None:
                    call_back()

        self.process_keys_held(pygame.key.get_pressed())



    def mouse_down_event(self, event):
        pass

    def mouse_up_event(self, event):
        pass

    def mouse_motion_event(self, event):
        pass

    def process_keys_held(self, keys_held):
        for key, value in self._registered_key_held_events.items():
            if keys_held[key]:
                value()


