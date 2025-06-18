"""
Exceptions module for TSE Analytics.

This module defines custom exceptions used throughout the TSE Analytics application.
"""


class InvalidSubscriber(Exception):
    """
    Exception raised when an invalid subscriber is used in the messaging system.

    This exception is raised when a subscriber that is not properly registered
    attempts to receive messages.
    """
    pass


class InvalidMessage(Exception):
    """
    Exception raised when an invalid message is sent in the messaging system.

    This exception is raised when a message with an invalid format or content
    is attempted to be sent through the messaging system.
    """
    pass
