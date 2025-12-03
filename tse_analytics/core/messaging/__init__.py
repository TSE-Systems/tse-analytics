from tse_analytics.core.messaging.messages import (
    AddToReportMessage as AddToReportMessage,
)
from tse_analytics.core.messaging.messages import (
    BinningMessage as BinningMessage,
)
from tse_analytics.core.messaging.messages import (
    DataChangedMessage as DataChangedMessage,
)
from tse_analytics.core.messaging.messages import (
    DatasetChangedMessage as DatasetChangedMessage,
)
from tse_analytics.core.messaging.messages import (
    DatatableChangedMessage as DatatableChangedMessage,
)
from tse_analytics.core.messaging.messages import (
    ReportsChangedMessage as ReportsChangedMessage,
)
from tse_analytics.core.messaging.messages import (
    SelectedTreeItemChangedMessage as SelectedTreeItemChangedMessage,
)
from tse_analytics.core.messaging.messages import (
    WorkspaceChangedMessage as WorkspaceChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener as MessengerListener

__messenger = Messenger()


subscribe = __messenger.subscribe
broadcast = __messenger.broadcast
is_subscribed = __messenger.is_subscribed
get_handler = __messenger.get_handler
unsubscribe = __messenger.unsubscribe
unsubscribe_all = __messenger.unsubscribe_all
