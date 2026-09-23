---
name: blender-efficient-modeling
description: Create, modify, UV-map, texture, validate, and deliver Blender assets or modular scenes with minimal context and deterministic CLI execution. Use by default for direct Blender generation, including detailed reference-driven assets, repeated variants, and assembled layouts; load broader Blender skills only when a requested specialist workflow is absent here.
---

# Blender Efficient Modeling

Use one compact contract, one staged build script, and targeted verification. Prefer Blender background CLI over interactive control unless the user explicitly needs the visible application.

## Route only what the task needs

- Read [references/geometry.md](references/geometry.md) for multi-part, modifier-heavy, Boolean, BMesh, curved, or topology-sensitive geometry.
- Read [references/uv-textures.md](references/uv-textures.md) only when UVs, image textures, baking, or packing are requested.
- Read [references/reference-modeling.md](references/reference-modeling.md) only when supplied images or dimensions are a source of truth.
- Read [references/modular-scenes.md](references/modular-scenes.md) for repeated assets, configurable variants, grids, settlements, kit-based scenes, or collection/object instancing.
- Read [references/scene-render.md](references/scene-render.md) only when a preview, composed scene, lighting, camera, or final render is required.
- Read [references/validation.md](references/validation.md) when defining a custom inspection spec or recovering from a failed build.

Do not automatically load `text-to-blender`, `blender-pro-workflow`, `blender-skill-harmonizer`, or the full modeling/material/lighting/camera/rendering stack. Load a specialist skill only for a requirement this skill and its focused references do not cover.

## Execution contract

1. Inspect the installed Blender version and use its executable directly. For background work, do not load Flue.
2. Translate the request into a small quality contract: required parts, dimensions or proportions, topology/UV/texture requirements, output files, and visual evidence. When comparing workflows or reproducing an exact layout, freeze the measurable contract before implementation and disallow undeclared creative additions.
3. Author one fresh staged build script. Preserve accepted stages instead of regenerating the scene after a local failure. For repeated scenes, validate 3–5 simple variants or one complex prototype batch before placement; share mesh data where edits should propagate.
4. Before mass placement, calculate a lightweight layout from declared footprints, clearances, forward axes, entrances, and reserved access areas. Reject forbidden overlap and out-of-bounds placement before creating detailed instances. For a controlled comparison, use the same accepted placement records in every implementation.
5. Use `scripts/blender_asset_runtime.py` for version-safe engine selection, transforms, normals, common UV mapping, image materials, packing, and the success marker.
6. Execute with `scripts/run_blender_job.py`. It rejects Blender's false-success case where a Python exception occurs but the process exits with code 0, then reopens the saved `.blend` using `scripts/inspect_blend.py`.
7. Inspect compact metrics and the evidence required at the current gate. Fix only the failed stage and invalidate only dependent checks. Do not restart from scratch unless the saved state is invalid.
8. Return the `.blend`, requested exports/images, and concise verification metrics.

Build scripts must call `finalize_job(metrics)` only after their own geometry and assignment checks pass. The runner supplies output paths through environment variables and accepts a JSON inspection spec.

```python
import os, sys
sys.path.insert(0, os.environ["CODEX_BLENDER_RUNTIME_DIR"])
from blender_asset_runtime import finalize_job

# Build and validate the requested asset here.
finalize_job({"mesh_count": 1, "stage": "complete"})
```

## Complexity policy

- Simple asset: build and verify in one pass.
- Complex hard-surface or assembled asset: derive a feature inventory and adjacency plan, block out named components, validate silhouette and negative spaces, then add modifiers/details/UVs without replacing accepted components.
- Repeated or modular scene: create each variant once, validate a variant matrix, approve a footprint plan, then place linked copies from deterministic records. Require exact instance counts, forbidden-overlap checks, access clearances, and spatial bounds before rendering.
- High-curvature or organic asset: use procedural mesh/BMesh where predictable; if sculpting or learned mesh generation is genuinely required, state that boundary and load the relevant specialist workflow.
- Reference-locked asset: measure the reference first and validate silhouettes/proportions with comparable views before declaring completion.

Cap blind retries. A retry must have a named failed check and a targeted correction. Preserve accepted prototypes, placement records, logs, and compact evidence; avoid full scene dumps and repeated screenshots when the relevant gate already passed.
