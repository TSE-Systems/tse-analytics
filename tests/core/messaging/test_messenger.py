"""Unit tests for the pub/sub :class:`Messenger`.

Every test uses a *fresh* ``Messenger()`` instance (never the module-level
singleton in ``core.messaging``) so there is no cross-test global state.
"""

import gc

import pytest
from tse_analytics.core.exceptions import InvalidMessage, InvalidSubscriber
from tse_analytics.core.messaging.messages import Message
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener


class _Base(Message):
    pass


class _Derived(_Base):
    pass


class _Other(Message):
    pass


class _Recorder(MessengerListener):
    """A listener that records every message it is notified about."""

    def __init__(self):
        self.received: list[Message] = []

    def register_to_messenger(self, messenger):
        messenger.subscribe(self, Message, self.notify)

    def notify(self, message):
        self.received.append(message)


@pytest.fixture
def messenger():
    return Messenger()


@pytest.fixture
def recorder():
    return _Recorder()


# --- delivery ----------------------------------------------------------------


def test_subscribe_and_broadcast_delivers(messenger, recorder):
    messenger.subscribe(recorder, _Base, recorder.notify)
    message = _Base(sender="x")
    messenger.broadcast(message)
    assert recorder.received == [message]


def test_default_handler_is_notify(messenger, recorder):
    messenger.subscribe(recorder, _Base)  # no handler -> subscriber.notify
    message = _Base("x")
    messenger.broadcast(message)
    assert recorder.received == [message]


def test_subclass_message_matches_superclass_subscription(messenger, recorder):
    messenger.subscribe(recorder, _Base)
    message = _Derived("x")
    messenger.broadcast(message)
    assert recorder.received == [message]


def test_unrelated_message_not_delivered(messenger, recorder):
    messenger.subscribe(recorder, _Base)
    messenger.broadcast(_Other("x"))
    assert recorder.received == []


def test_most_specific_handler_wins(messenger, recorder):
    calls: list[str] = []
    messenger.subscribe(recorder, _Base, lambda m: calls.append("base"))
    messenger.subscribe(recorder, _Derived, lambda m: calls.append("derived"))

    messenger.broadcast(_Derived("x"))
    assert calls == ["derived"]  # most-subclassed subscription selected

    calls.clear()
    messenger.broadcast(_Base("x"))
    assert calls == ["base"]  # _Derived is not a superclass of _Base


def test_filter_blocks_nonmatching_messages(messenger, recorder):
    messenger.subscribe(recorder, _Base, recorder.notify, filter=lambda m: getattr(m, "keep", False))
    blocked = _Base("blocked")
    blocked.keep = False
    kept = _Base("kept")
    kept.keep = True

    messenger.broadcast(blocked)
    messenger.broadcast(kept)
    assert recorder.received == [kept]


# --- subscription bookkeeping ------------------------------------------------


def test_is_subscribed_and_get_handler(messenger, recorder):
    assert not messenger.is_subscribed(recorder, _Base)
    messenger.subscribe(recorder, _Base, recorder.notify)
    assert messenger.is_subscribed(recorder, _Base)

    handler = messenger.get_handler(recorder, _Base)
    assert handler is not None
    handler(_Base("x"))  # reconstructed handler still drives the recorder
    assert len(recorder.received) == 1


def test_get_handler_none_subscriber_returns_none(messenger):
    assert messenger.get_handler(None, _Base) is None


def test_unsubscribe_stops_delivery(messenger, recorder):
    messenger.subscribe(recorder, _Base, recorder.notify)
    messenger.unsubscribe(recorder, _Base)
    messenger.broadcast(_Base("x"))
    assert recorder.received == []


def test_unsubscribe_all(messenger, recorder):
    messenger.subscribe(recorder, _Base, recorder.notify)
    messenger.subscribe(recorder, _Other, recorder.notify)
    messenger.unsubscribe_all(recorder)
    messenger.broadcast(_Base("x"))
    messenger.broadcast(_Other("x"))
    assert recorder.received == []


# --- validation --------------------------------------------------------------


def test_subscribe_rejects_non_listener(messenger):
    with pytest.raises(InvalidSubscriber):
        messenger.subscribe(object(), _Base)


def test_subscribe_rejects_non_message_class(messenger, recorder):
    with pytest.raises(InvalidMessage):
        messenger.subscribe(recorder, object)


# --- pause / ignore context managers -----------------------------------------


def test_delay_callbacks_queues_then_flushes(messenger, recorder):
    messenger.subscribe(recorder, _Base, recorder.notify)
    with messenger.delay_callbacks():
        messenger.broadcast(_Base("a"))
        messenger.broadcast(_Base("b"))
        assert recorder.received == []  # queued while paused
    assert len(recorder.received) == 2  # flushed on exit


def test_ignore_callbacks_suppresses_only_that_type(messenger, recorder):
    messenger.subscribe(recorder, _Base, recorder.notify)
    messenger.subscribe(recorder, _Other, recorder.notify)
    with messenger.ignore_callbacks(_Base):
        messenger.broadcast(_Base("ignored"))
        messenger.broadcast(_Other("kept"))
    assert len(recorder.received) == 1  # only _Other got through
    messenger.broadcast(_Base("now-delivered"))
    assert len(recorder.received) == 2


# --- constructor registration ------------------------------------------------


def test_constructor_registers_listeners():
    class _Listener(MessengerListener):
        def __init__(self):
            self.registered = False

        def register_to_messenger(self, messenger):
            self.registered = True

        def notify(self, message):
            pass

    listener = _Listener()
    Messenger(listener)
    assert listener.registered


def test_constructor_rejects_non_listener():
    with pytest.raises(TypeError):
        Messenger(object())


# --- weakref-based auto-cleanup ----------------------------------------------


def test_garbage_collected_subscriber_is_dropped(messenger):
    received: list[Message] = []

    class _Ephemeral(MessengerListener):
        def register_to_messenger(self, m):
            pass

        def notify(self, message):
            received.append(message)

    subscriber = _Ephemeral()
    messenger.subscribe(subscriber, _Base, subscriber.notify)
    del subscriber
    gc.collect()

    messenger.broadcast(_Base("x"))
    assert received == []
