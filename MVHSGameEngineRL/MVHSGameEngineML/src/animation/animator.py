from MVHSGameEngineML.src.animation.animation_state import AnimationState
from MVHSGameEngineML.src.utilities.state_machine import StateMachine

class Animator:
    def __init__(self):
        self.state_machine = StateMachine(self)
        self.animation_states = {}


    def add_animation_state(self, name, animation_frames, time_per_frame=0.2):

        """
        Add a new animation state. Animation states should all be added at when the owning game object is loaded
        :param name: Name used to identify the animation state
        :param animation_frames: pygame surfaces - list of animation frames
        :param time_per_frame: time delay between frames
        """

        animation_state = AnimationState(name, animation_frames, time_per_frame)
        self.animation_states[name] = animation_state


    def change_animation(self, name, set_if_animation_already_active=False):

        """
        Change animation states
        Be default if the animation state is already active it will not be changed.
        """

        if name in self.animation_states:

            if self.state_machine.current_state is None:
                self.state_machine.change_state(self.animation_states[name])
                return

            if set_if_animation_already_active:
                self.state_machine.change_state(self.animation_states[name])
                return

            if self.state_machine.current_state != self.animation_states[name]:
                self.state_machine.change_state(self.animation_states[name])


    def update(self, dt):

        """
        update the animation state machine holding the animation states.
        Each animation state will update its animation frame
        """

        self.state_machine.update(dt)

    @property
    def current_animation_frame(self):
        return self.state_machine.current_state.current_frame




