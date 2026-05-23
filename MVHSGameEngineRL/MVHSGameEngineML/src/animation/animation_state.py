from MVHSGameEngineML.src.utilities.state_machine.state import State


class AnimationState(State):
    def __init__(self, name, animation_frames, time_per_frame):
        super().__init__()
        self.name = name
        self.animation_frames = animation_frames
        self.current_frame_index = None
        self.current_frame = None
        self.time_per_frame = time_per_frame
        self.current_frame_time = 0
        self.setup()


    def setup(self):

        """
        Prepare state to be updated by state machine
        """

        if self.animation_frames is not None and len(self.animation_frames) > 0:
            self.current_frame_index = 0
            self.current_frame = self.animation_frames[self.current_frame_index]


    def update(self, owner, dt):

        """
        Move through animation frames. Frame will loop automatically after last frame for animation state plays
        """

        super().update(owner, dt)

        if self.current_frame is None:
            return

        self.current_frame_time += dt

        # Set first animation frame as active after last one playes
        if self.current_frame_time >= self.time_per_frame:
            self.current_frame_time = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            if self.current_frame_index >= len(self.animation_frames):
                self.current_frame_index = 0

            self.current_frame = self.animation_frames[self.current_frame_index]


    def on_enter(self, owner):

        """
        Animation state is active. Animation will start playing from the first frame for the state
        """

        super().on_enter(owner)
        self.current_frame_index = 0
        self.current_frame_time = 0
        self.current_frame = self.animation_frames[self.current_frame_index]
