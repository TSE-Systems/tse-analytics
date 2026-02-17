import sys
from unittest.mock import MagicMock

# Mock resources_rc at module level so generated *_ui.py files
# (which use bare `import resources_rc`) can be imported during test collection.
sys.modules["resources_rc"] = MagicMock()
