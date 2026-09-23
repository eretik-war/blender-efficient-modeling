# Geometry modes

Read this reference only when the shape is more than a few independent primitives or requires topology decisions.

## Choose the least fragile construction

- Use transformed primitives for blockout and independent rigid parts.
- Use direct mesh vertices/faces or BMesh for exact profiles, lofts, panels, and repeated topology.
- Use Mirror, Array, Solidify, Bevel, and Subdivision when their parameters remain useful to the user; apply them only when export or downstream topology requires it.
- Use Boolean for deliberate cuts and unions. Verify the result for empty meshes, non-manifold edges, inverted normals, and unexpected disconnected islands.
- Prefer curves for cables, pipes, trims, and swept profiles; convert to mesh only when UV/export requires it.

## Complex assets

Split the model into stable named components with explicit responsibilities. A useful progression is primary silhouette, secondary forms, joints/cutouts, then small detail. Validate bounds and relative proportions after the first two stages. A failed detail stage must not delete accepted primary geometry.

Use symmetry where the design is symmetric. Keep a clear origin and axis convention before adding Mirror or Array. Apply transforms before operations whose width depends on object scale.

## Required mesh checks

- Non-empty vertices and polygons for every deliverable mesh.
- Finite coordinates and dimensions.
- Outward normals on closed surfaces.
- No accidental duplicate object names or hidden cutter objects in the deliverable set.
- No unapplied negative scale unless intentionally required.
- Manifoldness only when the requested asset must be watertight; open surfaces can be valid.
- Modifier order recorded when it affects the result.

Use a checkpoint `.blend` after an expensive accepted stage. Patch the smallest named stage after a failure.
