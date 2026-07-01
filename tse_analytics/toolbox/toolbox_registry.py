"""Decorator-based plugin registry for toolbox widgets.

Provides a ``@toolbox_plugin`` class-decorator that registers a widget class
with the :class:`ToolboxRegistry`.  :class:`ToolboxButton` reads the registry
at construction time to build its menus dynamically.

The registry is the single source of truth for *which* tools exist and *when*
they apply: the optional ``dataset_types`` / ``required_datatable_name`` /
``internal`` fields on :class:`ToolboxPluginInfo` drive menu visibility, so the
consumer (:class:`~tse_analytics.views.misc.toolbox_button.ToolboxButton`) needs
no hard-coded per-tool special-casing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class ToolboxWidget(Protocol):
    """Structural contract that registered toolbox widgets must satisfy.

    The only hard requirement is constructability from a single positional
    ``datatable`` argument; :class:`ToolboxButton` instantiates widgets via
    ``widget_class(datatable)``.  A ``title`` attribute is **optional** — the
    consumer falls back to the plugin label when it is absent (e.g.
    ``DataTableWidget`` exposes ``name`` instead of ``title``).

    This Protocol is a typing/documentation aid only; it is intentionally **not**
    ``@runtime_checkable``.  The registry validation enforces the real contract
    via :func:`inspect.signature` rather than ``isinstance`` (see the registry
    test), because a strict structural check cannot express "callable with one
    positional arg" for widgets whose second positional parameter is not
    ``parent`` (again, ``DataTableWidget``).
    """

    def __init__(self, datatable: Any, parent: Any | None = None) -> None: ...


@dataclass(frozen=True)
class ToolboxPluginInfo:
    """Metadata for a single registered toolbox widget."""

    category: str
    label: str
    icon: str
    widget_class: type
    order: int = 0
    # --- optional applicability / presentation metadata ---
    dataset_types: tuple[str, ...] | None = None
    """Dataset types this tool applies to (``None`` => any dataset type)."""
    required_datatable_name: str | None = None
    """Datatable name this tool requires (``None`` => any datatable, incl. ``None``)."""
    internal: bool = False
    """Whether the tool is gated behind internal/developer features (e.g. the AI menu)."""
    tooltip: str | None = None
    """Optional tooltip shown on the menu action."""

    def is_applicable(self, dataset: Any, datatable: Any | None) -> bool:
        """Whether this tool applies to the given dataset/datatable selection.

        Kept duck-typed (no ``Dataset``/``Datatable`` imports) so the registry
        stays dependency-light.
        """
        if self.dataset_types is not None and dataset.dataset_type not in self.dataset_types:
            return False
        if self.required_datatable_name is not None:
            if datatable is None or datatable.name != self.required_datatable_name:
                return False
        return True


class ToolboxRegistry:
    """Central store of all toolbox plugin registrations."""

    # Explicit category order – categories appear in this sequence.
    CATEGORY_ORDER: list[str] = [
        "AI",
        "Data",
        "Exploration",
        "Bivariate",
        "ANOVA",
        "Factor Analysis",
        "Chronobiology",
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


def toolbox_plugin(
    category: str,
    label: str,
    icon: str,
    order: int = 0,
    *,
    dataset_types: tuple[str, ...] | None = None,
    required_datatable_name: str | None = None,
    internal: bool = False,
    tooltip: str | None = None,
):
    """Class decorator that registers a widget with the toolbox registry.

    Usage::

        @toolbox_plugin(category="Exploration", label="Histogram", icon=":/icons/exploration.png")
        class HistogramWidget(ToolboxWidgetBase):
            ...

    The applicability keywords are optional; when omitted a tool applies to every
    dataset type and is shown unconditionally (the historical default)::

        @toolbox_plugin(
            category="IntelliCage",
            label="Transitions",
            icon=":/icons/...",
            dataset_types=("IntelliCage", "IntelliMaze"),
            required_datatable_name="Visits",
        )
        class TransitionsWidget(ToolboxWidgetBase):
            ...
    """

    def decorator(cls: type) -> type:
        registry.register(
            ToolboxPluginInfo(
                category,
                label,
                icon,
                cls,
                order,
                dataset_types=dataset_types,
                required_datatable_name=required_datatable_name,
                internal=internal,
                tooltip=tooltip,
            )
        )
        return cls

    return decorator


def validate_registry() -> list[str]:
    """Return a list of human-readable consistency issues in the registry.

    Cheap, runtime-safe checks only — duplicate ``(category, label)`` pairs and
    empty icon strings.  Never raises, so a malformed plugin degrades gracefully
    instead of breaking the Toolbox menu.  Deeper checks (contract conformance,
    completeness of the import manifest) live in the registry test.
    """
    issues: list[str] = []
    seen: set[tuple[str, str]] = set()
    for category, plugins in registry.get_plugins().items():
        for plugin in plugins:
            key = (category, plugin.label)
            if key in seen:
                issues.append(f"Duplicate toolbox plugin: category={category!r} label={plugin.label!r}")
            seen.add(key)
            if not plugin.icon:
                issues.append(f"Toolbox plugin has empty icon: category={category!r} label={plugin.label!r}")
    return issues
