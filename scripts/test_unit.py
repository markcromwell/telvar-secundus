"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_mana_gd_contract import *  # noqa: F401,F403
from tests.test_detect_magic_contract import *  # noqa: F401,F403
from tests.test_light_sphere_contract import *  # noqa: F401,F403
from tests.test_banishment_contract import *  # noqa: F401,F403
