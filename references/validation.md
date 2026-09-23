# Compact validation

The runner reopens the `.blend` and evaluates an optional JSON specification. Keep the specification limited to observable requirements.

Supported fields:

```json
{
  "mesh_count": 1,
  "required_objects": ["GEO-body"],
  "dimensions": {"GEO-body": [2.0, 1.0, 1.0]},
  "dimension_tolerance": 0.001,
  "uv_required_for": ["GEO-body"],
  "uv_bounds_0_1": true,
  "texture_required": true,
  "camera_count": 1,
  "active_camera_type": "PERSP",
  "applied_scale_for": ["GEO-body"]
}
```

Omit checks the user does not need. A texture is valid when its node has an image and that image is generated, packed, or points to an existing file. `uv_bounds_0_1` should be false or omitted for tiling and UDIM workflows.

On failure, inspect `checks` and the tail of the runner log. Correct the named failure only. If Blender exits 0 but no build-result marker exists, treat it as a Python exception or early termination and inspect the traceback; never accept the `.blend` based on process status alone.

For repeated layouts, add build-time checks for exact group count, variant coverage, per-group required roles, shared mesh-data count, non-overlapping plot bounds, and four review-image paths. Keep these metrics in `finalize_job`; the generic reopen inspector verifies file-level invariants while the build script owns domain-specific layout checks.

Run layout checks twice when placement matters: first against planned footprints before detailed generation, then against evaluated world-space bounds after placement. Keep allowed contacts explicit; ground contact and intentional stacked parts should not be reported as collisions.

For workflow comparisons, validate both outputs against one immutable contract. Match dimensions, required parts, placements, materials, camera parameters, and render settings within stated tolerances. Do not treat two plausible but different assets as equivalent evidence for the execution method.
