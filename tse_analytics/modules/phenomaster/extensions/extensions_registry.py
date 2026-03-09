from PySide6.QtGui import QIcon

from tse_analytics.modules.phenomaster.extensions.actimot.views.actimot_widget import ActimotWidget
from tse_analytics.modules.phenomaster.extensions.calo.views.calo_widget import CaloWidget
from tse_analytics.modules.phenomaster.extensions.drinkfeed.views.drinkfeed_widget import DrinkFeedWidget
from tse_analytics.modules.phenomaster.extensions.grouphousing.views.grouphousing_widget import GroupHousingWidget

EXTENSIONS_REGISTRY = {
    "calo_data": {
        "icon": QIcon(":/icons/icons8-gauge-16.png"),
        "widget": CaloWidget,
    },
    "drinkfeed_bin_data": {
        "icon": QIcon(":/icons/icons8-bottle-of-water-16.png"),
        "widget": DrinkFeedWidget,
    },
    "drinkfeed_raw_data": {
        "icon": QIcon(":/icons/icons8-bottle-of-water-16.png"),
        "widget": DrinkFeedWidget,
    },
    "actimot_data": {
        "icon": QIcon(":/icons/icons8-grid-16.png"),
        "widget": ActimotWidget,
    },
    "grouphousing_data": {
        "icon": QIcon(":/icons/icons8-structural-16.png"),
        "widget": GroupHousingWidget,
    },
}
