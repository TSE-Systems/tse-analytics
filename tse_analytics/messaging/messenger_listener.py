class MessengerListener:

    """
    The base class for any object that subscribes to messenger messages.
    This interface defines a single method, notify, that receives messages.
    """

    def register_to_messenger(self, messenger: "Messenger"):
        raise NotImplementedError

    def unregister(self, messenger: "Messenger"):
        """Default unregistration action. Calls messenger.unsubscribe_all on self"""
        messenger.unsubscribe_all(self)

    def notify(self, message):
        raise NotImplementedError("Message has no handler: %s" % message)
