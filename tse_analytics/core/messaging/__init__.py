from tse_analytics.core.messaging.messages import *
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener as MessengerListener

__messenger = Messenger()


subscribe = __messenger.subscribe
broadcast = __messenger.broadcast
is_subscribed = __messenger.is_subscribed
get_handler = __messenger.get_handler
unsubscribe = __messenger.unsubscribe
unsubscribe_all = __messenger.unsubscribe_all
