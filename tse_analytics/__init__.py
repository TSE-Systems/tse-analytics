"""TSE Analytics package."""

import os
import sys

# The generated *_ui.py modules import resources at top level (`import resources_rc`),
# which requires this package's own directory on sys.path. Running main.py as a script
# and the PyInstaller bundle both provide this implicitly; the installed console-script
# (`uv run tse-analytics`) does not, so add it explicitly here — this runs before any
# tse_analytics submodule (including main) is imported.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
