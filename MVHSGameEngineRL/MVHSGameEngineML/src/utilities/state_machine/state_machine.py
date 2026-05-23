

from MVHSGameEngineML.src.utilities.state_machine.state import State

class StateMachine:

    def __init__(self, owner):
        self.owner = owner
        self.current_state = None

    def change_state(self, next_state:State):

        """
        transition from one state to another
        :param next_state:
        :return:
        """

        if self.current_state is not None:
            self.current_state.on_exit(self.owner)

        self.current_state = next_state

        if self.current_state is not None:
            self.current_state.on_enter(self.owner)


    def update(self, dt):

        """
        =Update the state machine, current state update will be called.
        :return:
        """

        if self.current_state is not None:
            self.current_state.update(self.owner, dt)

