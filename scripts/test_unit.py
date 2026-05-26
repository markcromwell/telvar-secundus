"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_banishment_spell import *  # noqa: F401,F403
from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_victory_loot import *  # noqa: F401,F403
