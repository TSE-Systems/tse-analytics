"""Shared fixtures for core service and IO tests.

Provides a ``recorder`` that captures every message broadcast on the *global*
messenger — the channel the real services use. The ``make_dataset`` factory lives
in the top-level ``tests/conftest.py`` so pipeline/module tests can reuse it too.
"""

import pytest
from tse_analytics.core import messaging
from tse_analytics.core.messaging.messages import Message
from tse_analytics.core.messaging.messenger_listener import MessengerListener


@pytest.fixture
def recorder():
    """A listener subscribed to the global messenger, capturing all messages."""

    class _Recorder(MessengerListener):
        def __init__(self):
            self.messages: list[Message] = []

        def register_to_messenger(self, messenger):
            pass

        def notify(self, message):
            self.messages.append(message)

        def of_type(self, message_class):
            return [m for m in self.messages if isinstance(m, message_class)]

    rec = _Recorder()
    messaging.subscribe(rec, Message, rec.notify)
    yield rec
    messaging.unsubscribe_all(rec)
