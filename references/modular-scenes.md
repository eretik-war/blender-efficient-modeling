# Modular and repeated scenes

Read this reference for settlements, crowds, prop scatters, repeated architecture, configurable kits, grids, or any scene where a small variant library is placed many times.

## Separate definition from placement

Represent the scene with three compact data layers:

1. **variant definitions** — dimensions, optional parts, material palette, semantic name;
2. **prototype builders** — one parametric constructor per asset family;
3. **placement records** — variant id, transform, plot/group id, and small allowed overrides.

Build every requested variant once in a prototype area or collection. Validate that every variant is visibly distinct before placing the full layout. For exact repetitions, use linked object data or collection instances. Make unique mesh copies only when geometry actually differs.

Use deterministic placement. Derive variation from plot index or a recorded random seed; never depend on process-global random state. Keep origins and forward axes consistent so rotations do not move doors, gates, or attachments to the wrong side.

## Approve layout before instancing

Represent every prototype with a 2D footprint and optional reserved areas such as a garage approach, doorway clearance, pedestrian radius, or vehicle turning area. Produce placement records before detailed instancing. Check them against roads, plot boundaries, other reserved areas, and scene bounds. A top-view proof should expose ids and occupied regions.

Use the preflight placement records as input to the build script. After placement, compare world-space bounds with the expected footprint within a declared tolerance. A mesh can be vertically separated from a road and still be invalid on the plan; do not use 3D intersection alone as the layout gate.

For scenes with multiple asset families, review in this order: unique variants, one representative assembly, layout footprints, full placement. An accepted prototype remains unchanged unless a later requirement explicitly invalidates it.

## Variation without uncontrolled uniqueness

Use a limited variation grammar. Examples include footprint, roof type, porch, chimney position, garage width, fence material, gate side, palette, and one optional prop group. Each placed asset records its selected variant. Do not create twenty bespoke builders when four house definitions and three garage definitions satisfy the request.

Preserve recognizable family resemblance while making the declared variants easy to distinguish from review views. Repetition is successful when repeated items share topology/data and the placement records explain all visible differences.

## Staged validation

Before a final render, check:

- exact plot/group count and unique group ids;
- requested variant ids all appear, with a balanced distribution when no other distribution was requested;
- every plot contains its required asset families;
- linked repeats share mesh data where intended;
- no unexpected overlap between plot bounds, roads, or fences;
- no forbidden footprint or reserved-access overlap before or after instancing;
- all objects rest on the intended ground plane;
- scene bounds and camera framing include the whole layout;
- four evidence views for a large layout: two opposing oblique views, one aerial view, and one low street-level view.

If a check fails, patch placement records or the responsible prototype. Do not rebuild unrelated prototypes or the whole scene.
