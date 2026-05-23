

class State:

    def on_enter(self, owner):

        """
        Called when state becomes active, called on same frame as set active. update will be called next frame.
        """

        pass


    def on_exit(self, owner):

        """
        Called as soon as owning state machine changes to another state.
        """

        pass


    def update(self, owner, dt:float)->None:

        """
        Called every frame when state is the active state in owning state machine
        """

        pass