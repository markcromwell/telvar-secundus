"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
Live GitHub Pages smoke-check unit tests live in tests.test_validate_live.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_validate_live import *  # noqa: F401,F403
itch.io build packaging checks live in tests.test_itch_package.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_itch_package import *  # noqa: F401,F403
