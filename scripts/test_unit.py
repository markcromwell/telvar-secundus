"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_dialogue_sfx import *  # noqa: F401,F403
from tests.test_door_spell_combat_sfx import *  # noqa: F401,F403
from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_player_footsteps import *  # noqa: F401,F403
