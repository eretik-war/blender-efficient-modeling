from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import bmesh
import bpy


def reset_scene() -> None:
    bpy.context.preferences.filepaths.save_version = 0
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def deterministic_grid(count: int, columns: int, spacing=(1.0, 1.0), origin=(0.0, 0.0, 0.0)):
    """Return stable row-major placement coordinates without global random state."""
    if count < 0 or columns < 1:
        raise ValueError("count must be non-negative and columns must be positive")
    sx, sy = float(spacing[0]), float(spacing[1])
    ox, oy, oz = map(float, origin)
    rows = math.ceil(count / columns) if count else 0
    x0 = ox - (min(count, columns) - 1) * sx * 0.5 if count else ox
    y0 = oy - (rows - 1) * sy * 0.5 if rows else oy
    return [(x0 + (index % columns) * sx, y0 + (index // columns) * sy, oz) for index in range(count)]


def linked_duplicate(source, name: str, *, collection=None, location=None, rotation_euler=None, scale=None):
    """Create an object copy that shares source data for efficient exact repetition."""
    target_collection = collection or bpy.context.collection
    duplicate = source.copy()
    duplicate.data = source.data
    duplicate.name = name
    target_collection.objects.link(duplicate)
    if location is not None:
        duplicate.location = location
    if rotation_euler is not None:
        duplicate.rotation_euler = rotation_euler
    if scale is not None:
        duplicate.scale = scale
    return duplicate


def assert_variant_matrix(records, *, expected_count: int, required_variants: dict[str, set[str]]) -> None:
    if len(records) != expected_count:
        raise RuntimeError(f"Expected {expected_count} placement records, got {len(records)}")
    for field, expected in required_variants.items():
        actual = {str(record[field]) for record in records if field in record}
        missing = sorted(expected - actual)
        if missing:
            raise RuntimeError(f"Missing {field} variants: {missing}")


def configure_render_engine(scene=None) -> str:
    scene = scene or bpy.context.scene
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            return engine
        except (TypeError, ValueError):
            continue
    raise RuntimeError("No supported Blender render engine is available")


def _activate(obj) -> None:
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transforms(obj, *, location: bool = False, rotation: bool = True, scale: bool = True) -> None:
    _activate(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def recalculate_normals(obj) -> None:
    if obj.type != "MESH":
        raise TypeError(f"{obj.name} is not a mesh")
    mesh = obj.data
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        mesh.update()
    finally:
        bm.free()


def unwrap(obj, *, method: str = "smart", island_margin: float = 0.02, cube_size: float = 1.0) -> str:
    if obj.type != "MESH":
        raise TypeError(f"{obj.name} is not a mesh")
    _activate(obj)
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        bpy.ops.mesh.select_all(action="SELECT")
        if method == "smart":
            bpy.ops.uv.smart_project(island_margin=island_margin)
        elif method == "cube":
            bpy.ops.uv.cube_project(cube_size=cube_size)
        elif method == "unwrap":
            bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=island_margin)
        else:
            raise ValueError(f"Unsupported UV method: {method}")
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
    return obj.data.uv_layers.active.name


def _load_image(path: str | Path, colorspace: str):
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    image = bpy.data.images.load(str(resolved), check_existing=True)
    image.colorspace_settings.name = colorspace
    return image


def create_image_material(
    name: str,
    *,
    base_color: str | Path | None = None,
    roughness: str | Path | None = None,
    metallic: str | Path | None = None,
    normal: str | Path | None = None,
    default_base_color=(0.8, 0.8, 0.8, 1.0),
    default_roughness: float = 0.5,
):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = default_base_color
    bsdf.inputs["Roughness"].default_value = default_roughness
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    def image_node(label: str, path, colorspace: str):
        node = nodes.new("ShaderNodeTexImage")
        node.name = label
        node.label = label
        node.image = _load_image(path, colorspace)
        return node

    if base_color:
        node = image_node("Base Color", base_color, "sRGB")
        links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    if roughness:
        node = image_node("Roughness", roughness, "Non-Color")
        links.new(node.outputs["Color"], bsdf.inputs["Roughness"])
    if metallic:
        node = image_node("Metallic", metallic, "Non-Color")
        links.new(node.outputs["Color"], bsdf.inputs["Metallic"])
    if normal:
        node = image_node("Normal", normal, "Non-Color")
        normal_map = nodes.new("ShaderNodeNormalMap")
        links.new(node.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    return material


def pack_external_files() -> None:
    bpy.ops.file.pack_all()


def _json_default(value: Any):
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
        return list(value)
    return str(value)


def finalize_job(metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    blend_value = os.environ.get("CODEX_BLENDER_BLEND")
    result_value = os.environ.get("CODEX_BLENDER_BUILD_RESULT")
    if not blend_value or not result_value:
        raise RuntimeError("Runner environment is missing CODEX_BLENDER_BLEND or CODEX_BLENDER_BUILD_RESULT")
    blend_path = Path(blend_value).resolve()
    result_path = Path(result_value).resolve()
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    payload = {
        "ok": True,
        "blender_version": bpy.app.version_string,
        "blend": str(blend_path),
        "mesh_count": sum(1 for obj in bpy.context.scene.objects if obj.type == "MESH"),
        "object_count": len(bpy.context.scene.objects),
        "metrics": metrics or {},
    }
    temporary = result_path.with_suffix(result_path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")
    temporary.replace(result_path)
    print("CODEX_BLENDER_JOB_OK=" + json.dumps(payload, separators=(",", ":"), default=_json_default))
    return payload
