from pathlib import Path

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import ShowHelpMessage

LAYOUT_VERSION = 9
IS_RELEASE = Path("_internal").exists()


def show_help(sender, filename: str):
    docs_path = Path("_internal/docs") if IS_RELEASE else Path("../docs")
    path = docs_path / Path(filename)
    if path.exists():
        with open(path, encoding="utf-8") as file:
            content = file.read().rstrip()
            if content is not None:
                content = (
                    content.replace("](", "](_internal/docs/") if IS_RELEASE else content.replace("](", "](../docs/")
                )
                Manager.messenger.broadcast(ShowHelpMessage(sender, content))
