"""Validation tests for the toolbox plugin registry.

These exercise the *real* registry: importing ``tse_analytics.toolbox`` runs the
explicit import manifest in ``toolbox/__init__.py``, populating the singleton
``registry``.  The tests guarantee that every ``@toolbox_plugin`` widget is
discovered, uniquely identified, and satisfies the minimal contract the consumer
(:class:`~tse_analytics.views.misc.toolbox_button.ToolboxButton`) relies on —
i.e. constructable as ``widget_class(datatable)``.
"""

import inspect
import re
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

# Importing the package triggers the import manifest that populates the registry.
import tse_analytics.toolbox  # noqa: F401
from PySide6.QtWidgets import QWidget
from tse_analytics.toolbox.toolbox_registry import ToolboxPluginInfo, registry, validate_registry

_REPO_ROOT = Path(__file__).resolve().parents[2]
# Roots that may contain @toolbox_plugin-decorated widgets (add new module roots here).
_WIDGET_ROOTS = [
    _REPO_ROOT / "tse_analytics" / "toolbox",
    _REPO_ROOT / "tse_analytics" / "modules" / "intellicage" / "toolbox",
]
_DECORATOR_RE = re.compile(r"@toolbox_plugin\b")


def _all_plugins() -> list[ToolboxPluginInfo]:
    return [plugin for plugins in registry.get_plugins().values() for plugin in plugins]


def _decorated_widget_files() -> set[Path]:
    """Source files that contain a ``@toolbox_plugin`` decoration."""
    files: set[Path] = set()
    for root in _WIDGET_ROOTS:
        for path in root.rglob("*_widget.py"):
            if _DECORATOR_RE.search(path.read_text(encoding="utf-8")):
                files.add(path.resolve())
    return files


def test_registry_is_populated():
    assert _all_plugins(), "Toolbox registry is empty — the import manifest did not run."


def test_every_decorated_widget_is_registered():
    """Drift guard: a @toolbox_plugin widget missing from toolbox/__init__.py fails here."""
    decorated = _decorated_widget_files()
    registered = {
        Path(src).resolve() for p in _all_plugins() if (src := inspect.getsourcefile(p.widget_class)) is not None
    }
    missing = decorated - registered
    assert not missing, (
        "These @toolbox_plugin widgets are not registered — add an import to "
        f"tse_analytics/toolbox/__init__.py: {sorted(str(p) for p in missing)}"
    )


def test_no_duplicate_category_label():
    keys = [(p.category, p.label) for p in _all_plugins()]
    dupes = [key for key, count in Counter(keys).items() if count > 1]
    assert not dupes, f"Duplicate (category, label) pairs: {dupes}"


def test_unique_order_within_category():
    for category, plugins in registry.get_plugins().items():
        orders = [p.order for p in plugins]
        dupes = [order for order, count in Counter(orders).items() if count > 1]
        assert not dupes, f"Category {category!r} has duplicate order values: {dupes}"


@pytest.mark.parametrize("plugin", _all_plugins(), ids=lambda p: f"{p.category}.{p.label}")
def test_widget_satisfies_contract(plugin):
    """Every registered widget must be a QWidget constructible as ``widget_class(datatable)``."""
    widget_class = plugin.widget_class
    assert issubclass(widget_class, QWidget), f"{widget_class.__name__} is not a QWidget"

    params = list(inspect.signature(widget_class.__init__).parameters.values())[1:]  # drop self
    assert params, f"{widget_class.__name__}.__init__ takes no datatable argument"
    # Beyond the first (datatable) parameter, everything must be optional so that
    # widget_class(datatable) is a valid call (e.g. DataTableWidget's name="...").
    for param in params[1:]:
        optional = param.default is not inspect.Parameter.empty or param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )
        assert optional, (
            f"{widget_class.__name__}.__init__ requires {param.name!r}; not callable as widget_class(datatable)."
        )


@pytest.mark.parametrize("plugin", _all_plugins(), ids=lambda p: f"{p.category}.{p.label}")
def test_icon_is_non_empty(plugin):
    assert isinstance(plugin.icon, str) and plugin.icon, f"{plugin.label} has an empty icon"


def test_validate_registry_reports_no_issues():
    assert validate_registry() == []


# --- is_applicable -----------------------------------------------------------


def _dataset(dataset_type: str):
    return SimpleNamespace(dataset_type=dataset_type)


def _datatable(name: str):
    return SimpleNamespace(name=name)


def test_is_applicable_dataset_type_and_datatable_gate():
    plugin = ToolboxPluginInfo(
        "IntelliCage",
        "Transitions",
        ":/icons/x.png",
        object,
        dataset_types=("IntelliCage", "IntelliMaze"),
        required_datatable_name="Visits",
    )
    assert plugin.is_applicable(_dataset("IntelliCage"), _datatable("Visits"))
    assert plugin.is_applicable(_dataset("IntelliMaze"), _datatable("Visits"))
    assert not plugin.is_applicable(_dataset("PhenoMaster"), _datatable("Visits"))
    assert not plugin.is_applicable(_dataset("IntelliCage"), _datatable("Nosepokes"))
    assert not plugin.is_applicable(_dataset("IntelliCage"), None)


def test_is_applicable_default_applies_everywhere():
    plugin = ToolboxPluginInfo("Exploration", "Histogram", ":/icons/x.png", object)
    assert plugin.is_applicable(_dataset("PhenoMaster"), None)
    assert plugin.is_applicable(_dataset("IntelliCage"), _datatable("Visits"))
