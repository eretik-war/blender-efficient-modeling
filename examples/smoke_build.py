import os
import sys

import bpy

sys.path.insert(0, os.environ["CODEX_BLENDER_RUNTIME_DIR"])
from blender_asset_runtime import finalize_job, reset_scene

reset_scene()
bpy.ops.mesh.primitive_cube_add(size=1)
bpy.context.object.name = "Skill smoke cube"
finalize_job({"stage": "smoke", "expected_meshes": 1})
