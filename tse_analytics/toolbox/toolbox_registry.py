"""Decorator-based plugin registry for toolbox widgets.

Provides a ``@toolbox_plugin`` class-decorator that registers a widget class
with the :class:`ToolboxRegistry`.  :class:`ToolboxButton` reads the registry
at construction time to build its menus dynamically.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolboxPluginInfo:
    """Metadata for a single registered toolbox widget."""

    category: str
    label: str
    icon: str
    widget_class: type
    order: int = 0


class ToolboxRegistry:
    """Central store of all toolbox plugin registrations."""

    # Explicit category order – categories appear in this sequence.
    CATEGORY_ORDER: list[str] = [
        "Data",
        "Exploration",
        "Bivariate",
        "ANOVA",
        "Factor Analysis",
        "Circadian Analysis",
        "Time Series",
        "IntelliCage",
    ]

    def __init__(self) -> None:
        self._plugins: dict[str, list[ToolboxPluginInfo]] = {}

    def register(self, info: ToolboxPluginInfo) -> None:
        """Register a plugin with the registry."""
        self._plugins.setdefault(info.category, []).append(info)

    def get_plugins(self) -> dict[str, list[ToolboxPluginInfo]]:
        """Return plugins grouped by category, sorted by declared order.

        Categories follow :attr:`CATEGORY_ORDER`; any unlisted categories
        are appended alphabetically at the end.
        """
        ordered: dict[str, list[ToolboxPluginInfo]] = {}
        for cat in self.CATEGORY_ORDER:
            if cat in self._plugins:
                ordered[cat] = sorted(self._plugins[cat], key=lambda p: p.order)

        # Append any categories not in the explicit order list.
        for cat in sorted(self._plugins.keys()):
            if cat not in ordered:
                ordered[cat] = sorted(self._plugins[cat], key=lambda p: p.order)

        return ordered


# Module-level singleton used by the decorator and consumers.
registry = ToolboxRegistry()


def toolbox_plugin(category: str, label: str, icon: str, order: int = 0):
    """Class decorator that registers a widget with the toolbox registry.

    Usage::

        @toolbox_plugin(category="Exploration", label="Histogram", icon=":/icons/exploration.png")
        class HistogramWidget(ToolboxWidgetBase):
            ...
    """

    def decorator(cls: type) -> type:
        registry.register(ToolboxPluginInfo(category, label, icon, cls, order))
        return cls

    return decorator
