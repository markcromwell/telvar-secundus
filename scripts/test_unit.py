"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_enemy_scripts import *  # noqa: F401,F403
from tests.test_enemy_scenes_and_stats import *  # noqa: F401,F403
