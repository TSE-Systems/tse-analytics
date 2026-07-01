"""Round-trip tests for the DuckDB workspace persistence layer (``core/io/storage``)."""

from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.io.storage import load_workspace, save_workspace


def _save_and_load(tmp_path, workspace: Workspace) -> Workspace:
    path = str(tmp_path / "ws.duckdb")
    save_workspace(path, workspace)
    return load_workspace(path)


def _workspace_with(dataset, name="My Workspace") -> Workspace:
    ws = Workspace(name=name)
    ws.datasets[dataset.id] = dataset
    return ws


def test_roundtrip_preserves_workspace_and_dataset(tmp_path, make_dataset):
    dataset = make_dataset("Experiment A")
    ws = _workspace_with(dataset)

    loaded = _save_and_load(tmp_path, ws)

    assert loaded.name == "My Workspace"
    assert loaded.id == ws.id
    assert len(loaded.datasets) == 1

    loaded_ds = next(iter(loaded.datasets.values()))
    assert loaded_ds.id == dataset.id
    assert loaded_ds.name == "Experiment A"
    assert loaded_ds.dataset_type == "PhenoMaster"
    assert set(loaded_ds.animals) == {"A1", "A2"}
    assert "Group" in loaded_ds.factors  # custom factor survived serialization


def test_roundtrip_preserves_datatable_values(tmp_path, make_dataset):
    dataset = make_dataset()
    loaded = _save_and_load(tmp_path, _workspace_with(dataset))

    original_dt = dataset.datatables["Main"]
    loaded_dt = next(iter(loaded.datasets.values())).datatables["Main"]

    assert list(loaded_dt.df.columns) == list(original_dt.df.columns)
    assert len(loaded_dt.df) == len(original_dt.df)
    # Values survive; DuckDB may normalize dtypes and does not guarantee row order.
    assert sorted(loaded_dt.df["Weight"].astype("float").tolist()) == [25.0, 25.5, 26.0, 26.5]
    assert sorted(loaded_dt.df["Animal"].astype("string").tolist()) == ["A1", "A1", "A2", "A2"]
    assert "Weight" in loaded_dt.variables


def test_roundtrip_preserves_reports(tmp_path, make_dataset):
    dataset = make_dataset()
    loaded = _save_and_load(tmp_path, _workspace_with(dataset))

    loaded_ds = next(iter(loaded.datasets.values()))
    assert "R1" in loaded_ds.reports
    assert loaded_ds.reports["R1"].content == "<p>report</p>"


def test_save_overwrites_existing_file(tmp_path, make_dataset):
    dataset = make_dataset()
    ws = _workspace_with(dataset)
    path = str(tmp_path / "ws.duckdb")

    save_workspace(path, ws)
    save_workspace(path, ws)  # second save must overwrite, not raise

    loaded = load_workspace(path)
    assert len(loaded.datasets) == 1
