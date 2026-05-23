
from MVHSGameEngineML.src.core.game_object import GameObject
from MVHSGameEngineML.src.input.key_input_type import KeyInputType

# class InputType(Enum):
#     KEY_DOWN = 0
#     KEY_UP = 1
#     KEY_HELD = 2
#     MOUSE_BUTTON_1 = 3
#     MOUSE_BUTTON_2 = 4
#     MOUSE_BUTTON_3 = 5
#     MOUSE_MOTION = 6

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)

    def get_input_manager(self):
        return self.world.player_input_manager

    def register_key_input(self, input_type: KeyInputType, key, callback_method):
        input_manager = self.get_input_manager()

        if input_type == KeyInputType.KEY_DOWN:
            input_manager.register_key_down(key, callback_method)
        elif input_type == KeyInputType.KEY_UP:
            input_manager.register_key_up(key, callback_method)
        elif input_type == KeyInputType.KEY_HELD:
            input_manager._register_key_held(key, callback_method)


