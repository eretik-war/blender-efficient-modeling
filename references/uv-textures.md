# UV and image textures

Read this reference only when the output needs UVs, image textures, texture baking, or packed resources.

## UV choice

- Box-like isolated props: cube projection is usually predictable.
- Mixed hard-surface parts: mark meaningful seams when placement matters; otherwise use Smart UV Project with a nonzero island margin.
- Cylinders and pipes: seam along the least visible side plus cap separation.
- Reference atlas or authored layout: construct or fit UVs explicitly; do not replace it with Smart UV Project.

Apply object scale before unwrapping. Verify that required mesh objects have an active UV layer, every polygon loop has finite UV coordinates, and islands meet the requested 0–1 or UDIM policy. Do not enforce 0–1 when tiling is intentional.

## Material contract

Use Principled BSDF for ordinary game/web materials. Connect only maps the task provides or requests.

- Base color/emissive: `sRGB`.
- Roughness, metallic, normal, AO, masks: `Non-Color`.
- Normal images pass through a Normal Map node before Principled Normal.
- An Image Texture node without an assigned image is a failed check.
- A linked external file must exist, be made relative to the `.blend`, or be packed when portability is requested.

Procedural materials do not become ordinary image textures during glTF export. Bake them only when the target format requires image maps.

Use `create_image_material()` for the common map set and `pack_external_files()` only when packing is requested. For generated textures, create the texture separately, then give Blender a stable absolute path; do not regenerate it during every Blender retry.
