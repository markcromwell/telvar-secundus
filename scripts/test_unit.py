"""Fast unit smoke entrypoint for CI (see worker Execution Contract).

Godot project filesystem checks live in tests.test_godot_config.
"""

from tests.test_godot_config import *  # noqa: F401,F403
from tests.test_veneficturis_main_hall_passage import *  # noqa: F401,F403
from tests.test_web_export_readiness import *  # noqa: F401,F403
