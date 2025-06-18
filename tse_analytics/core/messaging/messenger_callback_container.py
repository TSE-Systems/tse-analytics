import weakref
from functools import partial


class MessengerCallbackContainer:
    """
    A list-like container for callback functions. We need to be careful with
    storing references to methods, because if a callback method is on a class
    which contains both the callback and a callback property, a circular
    reference is created which results in a memory leak. Instead, we need to use
    a weak reference which results in the callback being removed if the instance
    is destroyed. This container class takes care of this automatically.

    Adapted from echo.CallbackContainer.
    """

    def __init__(self):
        self.callbacks = {}

    def _wrap(self, handler, filter):
        """
        Given a function/method, this will automatically wrap a method using
        weakref to avoid circular references.
        """

        if not callable(handler):
            raise TypeError("Only callable handlers can be stored in CallbackContainer")

        if filter is not None and not callable(filter):
            raise TypeError("Only callable filters can be stored in CallbackContainer")

        if self.is_bound_method(handler):
            # We are dealing with a bound method. Method references aren't
            # persistent, so instead we store a reference to the function
            # and instance.

            value = (weakref.ref(handler.__func__), weakref.ref(handler.__self__, self._auto_remove))

        else:
            value = (handler, None)

        if self.is_bound_method(filter):
            # We are dealing with a bound method. Method references aren't
            # persistent, so instead we store a reference to the function
            # and instance.

            value += (weakref.ref(filter.__func__), weakref.ref(filter.__self__, self._auto_remove))

        else:
            value += (filter, None)

        return value

    def _auto_remove(self, method_instance):
        """Called when weakref detects that the instance on which a method was
        defined has been garbage collected.

        This method removes all callbacks that reference the garbage-collected instance.

        :param method_instance: The instance that was garbage collected
        """
        remove = []
        for key, value in self.callbacks.items():
            if value[1] is method_instance or value[3] is method_instance:
                remove.append(key)
        for key in remove:
            self.callbacks.pop(key)

    def __contains__(self, message_class):
        """Check if a message class is in the container.

        :param message_class: The message class to check for
        :return: True if the message class is in the container, False otherwise
        """
        return message_class in self.callbacks

    def __getitem__(self, message_class):
        """Get the handler and filter for a message class.

        This method reconstructs the handler and filter functions from their
        weak references.

        :param message_class: The message class to get the handler and filter for
        :return: A tuple of (handler, filter)
        """
        callback = self.callbacks[message_class]

        if callback[1] is None:
            result = (callback[0],)
        else:
            func = callback[0]()
            inst = callback[1]()
            result = (partial(func, inst),)

        if callback[3] is None:
            result += (callback[2],)
        else:
            func = callback[2]()
            inst = callback[3]()
            result += (partial(func, inst),)

        return result

    def __iter__(self):
        """Iterate over all message classes in the container.

        :yield: The handler and filter for each message class
        """
        for message_class in self.callbacks:
            yield self[message_class]

    def __len__(self):
        """Get the number of message classes in the container.

        :return: The number of message classes
        """
        return len(self.callbacks)

    def keys(self):
        """Get all message classes in the container.

        :return: A view of all message classes
        """
        return self.callbacks.keys()

    @staticmethod
    def is_bound_method(func):
        """Check if a function is a bound method.

        A bound method is a method that is bound to an instance of a class.

        :param func: The function to check
        :return: True if the function is a bound method, False otherwise
        """
        return hasattr(func, "__func__") and getattr(func, "__self__", None) is not None

    def __setitem__(self, message_class, value):
        """Set the handler and filter for a message class.

        :param message_class: The message class to set the handler and filter for
        :param value: A tuple of (handler, filter)
        """
        handler, filter = value
        self.callbacks[message_class] = self._wrap(handler, filter)

    def pop(self, message_class):
        """Remove a message class from the container and return its handler and filter.

        :param message_class: The message class to remove
        :return: The handler and filter for the message class
        """
        return self.callbacks.pop(message_class)

    def remove_handler(self, handler):
        """Remove all message classes that use the given handler.

        :param handler: The handler to remove
        """
        if self.is_bound_method(handler):
            for message_class in sorted(self.callbacks):
                callback = self.callbacks[message_class]
                if callback[1] is not None and handler.__func__ is callback[0]() and handler.__self__ is callback[1]():
                    self.callbacks.pop(callback)
        else:
            for message_class in sorted(self.callbacks):
                callback = self.callbacks[message_class]
                if callback[1] is None and handler is callback[0]:
                    self.callbacks.pop(callback)
