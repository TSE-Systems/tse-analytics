from collections import Counter
from contextlib import contextmanager
from inspect import getmro
from weakref import WeakKeyDictionary

from tse_analytics.core.exceptions import InvalidMessage, InvalidSubscriber
from tse_analytics.messaging.messages import Message
from tse_analytics.messaging.messenger_callback_container import MessengerCallbackContainer
from tse_analytics.messaging.messenger_listener import MessengerListener


class Messenger:
    """The messenger manages communication between subscribers.

    Objects :func:`subscribe` to receive specific message types. When
    a message is passed to :func:`broadcast`, the messenger observes the
    following protocol:

        * For each subscriber, it looks for a message class
          subscription that is a superclass of the input message type
          (if several are found, the most-subclassed one is chosen)

        * If one is found, it calls the subscriptions filter(message)
          class (if provided)

        * If filter(message) == True, it calls handler(message)
          (or notify(message) if handler wasn't provided).

    """

    def __init__(self, *args):
        """
        Any arguments that are passed to Messenger will be registered
        to the new messenger object.
        """
        # Dictionary of subscriptions
        self._subscriptions = WeakKeyDictionary()

        self._paused = False
        self._queue = []

        self._ignore = Counter()

        listeners = set(filter(lambda x: isinstance(x, MessengerListener), args))
        if set(listeners) != set(args):
            raise TypeError("Inputs must be MessengerListener, data, subset, or data collection objects")

        for listener in listeners:
            listener.register_to_messenger(self)

    def subscribe(self, subscriber, message_class, handler=None, filter=lambda x: True):
        """Subscribe an object to a type of message class.

        :param subscriber: The subscribing object
        :type subscriber: :class:`~glue.core.messenger.MessengerListener`

        :param message_class: A :class:`~glue.core.message.Message` class
                              to subscribe to

        :param handler:
           An optional function of the form handler(message) that will
           receive the message on behalf of the subscriber. If not provided,
           this defaults to the MessengerListener's notify method


        :param filter:
           An optional function of the form filter(message). Messages
           are only passed to the subscriber if filter(message) == True.
           The default is to always pass messages.


        Raises:
            InvalidMessage: If the input class isn't a
            :class:`~glue.core.message.Message` class

            InvalidSubscriber: If the input subscriber isn't a
            MessengerListener object.

        """
        if not isinstance(subscriber, MessengerListener):
            raise InvalidSubscriber("Subscriber must be a MessengerListener: %s" % type(subscriber))
        if not isinstance(message_class, type) or not issubclass(message_class, Message):
            raise InvalidMessage("message class must be a subclass of Message: %s" % type(message_class))
        # logging.getLogger(__name__).debug("Subscribing %s to %s", subscriber, message_class.__name__)

        if not handler:
            handler = subscriber.notify

        if subscriber not in self._subscriptions:
            self._subscriptions[subscriber] = MessengerCallbackContainer()

        self._subscriptions[subscriber][message_class] = handler, filter

    def is_subscribed(self, subscriber, message):
        """
        Test whether the subscriber has subscribed to a given message class

        :param subscriber: The subscriber to test
        :param message: The message class to test

        Returns:

            True if the subscriber/message pair have been subscribed to the messenger

        """
        return subscriber in self._subscriptions and message in self._subscriptions[subscriber]

    def get_handler(self, subscriber, message):
        if subscriber is None:
            return None
        try:
            return self._subscriptions[subscriber][message][0]
        except KeyError:
            return None

    def unsubscribe(self, subscriber, message):
        """
        Remove a (subscriber,message) pair from subscription list.
        The handler originally attached to the subscription will
        no longer be called when broadcasting messages of type message
        """
        if subscriber not in self._subscriptions:
            return
        if message in self._subscriptions[subscriber]:
            self._subscriptions[subscriber].pop(message)

    def unsubscribe_all(self, subscriber):
        """
        Unsubscribe the object from any subscriptions.
        """
        if subscriber in self._subscriptions:
            self._subscriptions.pop(subscriber)

    def _find_handlers(self, message):
        """Yields all (subscriber, handler) pairs that should receive a message"""
        # self._subscriptions:
        # subscriber => { message type => (filter, handler)}

        # loop over subscribed objects
        for subscriber, subscriptions in list(self._subscriptions.items()):
            # subscriptions to message or its superclasses
            messages = [msg for msg in subscriptions.keys() if issubclass(type(message), msg)]

            if len(messages) == 0:
                continue

            # narrow to the most-specific message
            candidate = max(messages, key=_mro_count)

            handler, test = subscriptions[candidate]
            if test(message):
                yield subscriber, handler

    @contextmanager
    def ignore_callbacks(self, ignore_type):
        self._ignore[ignore_type] += 1
        try:
            yield
        finally:
            self._ignore[ignore_type] -= 1

    @contextmanager
    def delay_callbacks(self):
        self._paused = True
        try:
            yield
        finally:
            self._paused = False
            # TODO: could de-duplicate messages here
            for message in self._queue:
                self.broadcast(message)
            self._queue = []

    def broadcast(self, message):
        """Broadcasts a message to all subscribed objects.

        :param message: The message to broadcast
        :type message: :class:`~glue.core.message.Message`
        """
        if self._ignore.get(type(message), 0) > 0:
            return
        elif self._paused:
            self._queue.append(message)
        else:
            # logging.getLogger(__name__).debug("Broadcasting %s", message)
            for subscriber, handler in self._find_handlers(message):
                handler(message)

    def __getstate__(self):
        """Return a picklable representation of the messenger

        Note: Only objects in glue.core are currently supported
        as pickleable. Thus, any subscriptions from objects outside
        glue.core will note be saved or restored
        """
        result = self.__dict__.copy()
        result["_subscriptions"] = self._subscriptions.copy()
        for s in self._subscriptions:
            try:
                module = s.__module__
            except AttributeError:
                module = ""
            if not module.startswith("glue.core"):
                # logging.getLogger(__name__).debug(f"Pickle warning: Messenger removing subscription to {s}")
                result["_subscriptions"].pop(s)
        return result


def _mro_count(obj):
    return len(getmro(obj))
