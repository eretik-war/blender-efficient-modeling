# Scene and render evidence

Read this reference only when a preview, lighting, camera composition, scene assembly, or final render is part of the request.

For an ordinary verification preview, use a deterministic neutral preset rather than loading full camera, lighting, and rendering skills:

- EEVEE through `configure_render_engine()`;
- neutral world background;
- one perspective camera fitted to evaluated object bounds;
- broad key and fill lights, with an optional rim for dark silhouettes;
- modest resolution and samples;
- PNG output and explicit dimensions;
- no depth of field unless requested.

Exclude hidden cutters, helpers, and oversized ground planes from camera fitting. Verify that the visible subject is centered and occupies a useful fraction of the frame. Decode the produced PNG and check dimensions; use luminance or dark-pixel gates only when visibility is a requirement.

Load specialist camera/lighting/rendering guidance only for an artistic or technical requirement such as cinematic composition, HDRI matching, Cycles realism, depth of field, compositing, animation, or color-managed final delivery.
