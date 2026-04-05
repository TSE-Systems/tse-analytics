from PySide6.QtGui import QIcon

from tse_analytics.modules.phenomaster.extensions.actimot.views.actimot_widget import ActimotWidget
from tse_analytics.modules.phenomaster.extensions.calo.views.calo_widget import CaloWidget
from tse_analytics.modules.phenomaster.extensions.drinkfeed.views.drinkfeed_widget import DrinkFeedWidget
from tse_analytics.modules.phenomaster.extensions.grouphousing.views.grouphousing_widget import GroupHousingWidget
from tse_analytics.modules.phenomaster.io.tse_import_settings import (
    ACTIMOT_RAW_TABLE,
    CALO_BIN_TABLE,
    DRINKFEED_BIN_TABLE,
    DRINKFEED_RAW_TABLE,
    GROUP_HOUSING_TABLE,
)

EXTENSIONS_REGISTRY = {
    CALO_BIN_TABLE: {
        "icon": QIcon(":/icons/icons8-gauge-16.png"),
        "widget": CaloWidget,
    },
    DRINKFEED_BIN_TABLE: {
        "icon": QIcon(":/icons/icons8-bottle-of-water-16.png"),
        "widget": DrinkFeedWidget,
    },
    DRINKFEED_RAW_TABLE: {
        "icon": QIcon(":/icons/icons8-bottle-of-water-16.png"),
        "widget": DrinkFeedWidget,
    },
    ACTIMOT_RAW_TABLE: {
        "icon": QIcon(":/icons/icons8-grid-16.png"),
        "widget": ActimotWidget,
    },
    GROUP_HOUSING_TABLE: {
        "icon": QIcon(":/icons/icons8-structural-16.png"),
        "widget": GroupHousingWidget,
    },
}
