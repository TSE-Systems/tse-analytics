"""
Animal Gate extension for the IntelliMaze module.

This extension provides functionality for importing, processing, and analyzing data
from Animal Gate devices in IntelliMaze experiments. Animal Gates are used to control
animal access to different areas of the experiment setup and to record animal movements.

The extension is organized into two submodules:
- data: Contains data models and structures
- io: Contains input/output operations
"""

from . import io, data
from .data.animal_gate_data import EXTENSION_NAME
