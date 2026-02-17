"""SQLite database introspection utilities."""

from pathlib import Path

import connectorx as cx


def get_available_sqlite_tables(path: Path) -> list[str]:
    """Get a list of all table names in a SQLite database file.

    This function connects to the specified SQLite database file and retrieves
    the names of all tables defined in the database.

    Args:
        path: The path to the SQLite database file.

    Returns:
        A list of strings containing the names of all tables in the database.
    """
    df = cx.read_sql(
        f"sqlite:///{path}",
        "SELECT name FROM sqlite_master WHERE type='table';",
        return_type="pandas",
    )
    return df["name"].tolist()
