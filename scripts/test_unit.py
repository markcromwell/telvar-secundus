"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_wings_enter_scripts import *  # noqa: F401,F403
from tests.test_final_cutscene_epilogue import *  # noqa: F401,F403
