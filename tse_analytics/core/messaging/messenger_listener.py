class MessengerListener:
    """
    The base class for any object that subscribes to messenger messages.
    This interface defines a single method, notify, that receives messages.
    """

    def register_to_messenger(self, messenger):
        """Register this listener to a messenger.

        This method should be implemented by subclasses to register
        the listener to the messenger with appropriate message subscriptions.

        :param messenger: The messenger to register to
        :raises NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError

    def unregister(self, messenger):
        """Unregister this listener from a messenger.

        Default unregistration action. Calls messenger.unsubscribe_all on self.

        :param messenger: The messenger to unregister from
        """
        messenger.unsubscribe_all(self)

    def notify(self, message):
        """Handle a message received from a messenger.

        This method should be implemented by subclasses to handle
        messages received from the messenger.

        :param message: The message to handle
        :raises NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError(f"Message has no handler: {message}")
