"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_credits_phase import *  # noqa: F401,F403
from tests.test_save_menu_and_transition import *  # noqa: F401,F403
from tests.test_save_system import *  # noqa: F401,F403
