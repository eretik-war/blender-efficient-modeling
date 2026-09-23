from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy


def args_after_separator():
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def image_status(image):
    packed = bool(getattr(image, "packed_file", None))
    generated = image.source in {"GENERATED", "VIEWER"}
    path = Path(bpy.path.abspath(image.filepath)).resolve() if image.filepath else None
    exists = bool(path and path.is_file())
    return {"name": image.name, "path": str(path) if path else "", "packed": packed, "generated": generated, "valid": packed or generated or exists}


def uv_status(obj):
    layer = obj.data.uv_layers.active if obj.data.uv_layers else None
    if not layer:
        return {"exists": False, "finite": False, "bounds": None, "loop_count": 0}
    values = [(float(item.uv.x), float(item.uv.y)) for item in layer.data]
    finite = all(math.isfinite(u) and math.isfinite(v) for u, v in values)
    bounds = None
    if values:
        bounds = [min(u for u, _ in values), min(v for _, v in values), max(u for u, _ in values), max(v for _, v in values)]
    return {"exists": True, "finite": finite, "bounds": bounds, "loop_count": len(values), "name": layer.name}


def main():
    argv = args_after_separator()
    if not argv:
        raise SystemExit("Expected output JSON path after --")
    output = Path(argv[0]).resolve()
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8-sig")) if len(argv) > 1 else {}
    scene = bpy.context.scene
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    cameras = [obj for obj in scene.objects if obj.type == "CAMERA"]
    objects = {obj.name: obj for obj in scene.objects}
    uv = {obj.name: uv_status(obj) for obj in meshes}
    texture_nodes = []
    for material in bpy.data.materials:
        if not material.node_tree:
            continue
        for node in material.node_tree.nodes:
            if node.bl_idname == "ShaderNodeTexImage":
                texture_nodes.append({
                    "material": material.name,
                    "node": node.name,
                    "image": image_status(node.image) if node.image else None,
                })

    checks = []

    def add(name, ok, actual=None, expected=None):
        checks.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    if "mesh_count" in spec:
        add("mesh_count", len(meshes) == spec["mesh_count"], len(meshes), spec["mesh_count"])
    for name in spec.get("required_objects", []):
        add(f"object:{name}", name in objects, name in objects, True)
    tolerance = float(spec.get("dimension_tolerance", 0.001))
    for name, expected in spec.get("dimensions", {}).items():
        actual = list(objects[name].dimensions) if name in objects else None
        ok = actual is not None and len(actual) == len(expected) and all(abs(float(a) - float(b)) <= tolerance for a, b in zip(actual, expected))
        add(f"dimensions:{name}", ok, actual, expected)
    uv_targets = spec.get("uv_required_for", [])
    if spec.get("uv_required") is True:
        uv_targets = [obj.name for obj in meshes]
    for name in uv_targets:
        status = uv.get(name)
        add(f"uv:{name}", bool(status and status["exists"] and status["finite"] and status["loop_count"] > 0), status, "finite UV layer")
        if status and spec.get("uv_bounds_0_1"):
            bounds = status["bounds"]
            in_bounds = bool(bounds and bounds[0] >= -1e-5 and bounds[1] >= -1e-5 and bounds[2] <= 1.00001 and bounds[3] <= 1.00001)
            add(f"uv_bounds:{name}", in_bounds, bounds, [0, 0, 1, 1])
    if spec.get("texture_required"):
        add("texture_nodes_present", bool(texture_nodes), len(texture_nodes), ">=1")
    if texture_nodes:
        invalid = [item for item in texture_nodes if not item["image"] or not item["image"]["valid"]]
        add("texture_images_valid", not invalid, invalid, [])
    if "camera_count" in spec:
        add("camera_count", len(cameras) == spec["camera_count"], len(cameras), spec["camera_count"])
    if "active_camera_type" in spec:
        actual_type = scene.camera.data.type if scene.camera else None
        add("active_camera_type", actual_type == spec["active_camera_type"], actual_type, spec["active_camera_type"])
    for name in spec.get("applied_scale_for", []):
        actual = list(objects[name].scale) if name in objects else None
        ok = actual is not None and all(abs(float(value) - 1.0) <= 1e-5 for value in actual)
        add(f"applied_scale:{name}", ok, actual, [1, 1, 1])

    payload = {
        "ok": all(item["pass"] for item in checks),
        "blend": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "summary": {
            "objects": len(scene.objects),
            "meshes": len(meshes),
            "cameras": len(cameras),
            "vertices": sum(len(obj.data.vertices) for obj in meshes),
            "polygons": sum(len(obj.data.polygons) for obj in meshes),
            "texture_nodes": len(texture_nodes),
        },
        "checks": checks,
        "objects": [
            {"name": obj.name, "type": obj.type, "dimensions": [round(float(v), 6) for v in obj.dimensions], "uv": uv.get(obj.name)}
            for obj in scene.objects
        ],
        "textures": texture_nodes,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("CODEX_BLENDER_INSPECTION=" + json.dumps({"ok": payload["ok"], **payload["summary"]}, separators=(",", ":")))
    if not payload["ok"]:
        raise SystemExit(2)


main()
