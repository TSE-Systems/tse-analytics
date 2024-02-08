class MessengerListener:
    """
    The base class for any object that subscribes to messenger messages.
    This interface defines a single method, notify, that receives messages.
    """

    def register_to_messenger(self, messenger):
        raise NotImplementedError

    def unregister(self, messenger):
        """Default unregistration action. Calls messenger.unsubscribe_all on self"""
        messenger.unsubscribe_all(self)

    def notify(self, message):
        raise NotImplementedError(f"Message has no handler: {message}")
