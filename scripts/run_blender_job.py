from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")


def parser():
    result = argparse.ArgumentParser(description="Run one guarded Blender build and reopen verification")
    result.add_argument("--build-script", required=True, type=Path)
    result.add_argument("--blend", required=True, type=Path)
    result.add_argument("--work-dir", required=True, type=Path)
    result.add_argument("--spec", type=Path)
    result.add_argument("--blender", type=Path, default=DEFAULT_BLENDER)
    result.add_argument("--timeout", type=int, default=300)
    return result


def tail(text: str, limit: int = 3000) -> str:
    return text[-limit:] if len(text) > limit else text


def run_process(command, *, env, timeout):
    started = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, text=True, errors="replace", env=env, timeout=timeout)
    return completed, time.perf_counter() - started


def fail(reason, *, log_path: Path, build_seconds=0.0, verify_seconds=0.0):
    payload = {"ok": False, "reason": reason, "log": str(log_path), "build_seconds": round(build_seconds, 3), "verify_seconds": round(verify_seconds, 3)}
    print(json.dumps(payload, indent=2))
    return 1


def main():
    args = parser().parse_args()
    blender = args.blender.resolve()
    build_script = args.build_script.resolve()
    blend = args.blend.resolve()
    work = args.work_dir.resolve()
    spec = args.spec.resolve() if args.spec else None
    for path, label in ((blender, "Blender"), (build_script, "build script")):
        if not path.is_file():
            raise SystemExit(f"Missing {label}: {path}")
    if spec and not spec.is_file():
        raise SystemExit(f"Missing spec: {spec}")
    work.mkdir(parents=True, exist_ok=True)
    blend.parent.mkdir(parents=True, exist_ok=True)
    marker = work / "build_result.json"
    inspection = work / "inspection.json"
    log_path = work / "blender_job.log"
    for path in (marker, inspection):
        if path.exists():
            path.unlink()

    env = os.environ.copy()
    env["CODEX_BLENDER_BLEND"] = str(blend)
    env["CODEX_BLENDER_BUILD_RESULT"] = str(marker)
    env["CODEX_BLENDER_RUNTIME_DIR"] = str(HERE)
    start_wall = time.time()
    try:
        build, build_seconds = run_process(
            [str(blender), "--background", "--factory-startup", "--python", str(build_script)],
            env=env,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        log_path.write_text((exc.stdout or "") + "\n" + (exc.stderr or ""), encoding="utf-8")
        return fail("build timeout", log_path=log_path)
    build_log = build.stdout + "\n" + build.stderr
    log_path.write_text("=== BUILD ===\n" + build_log, encoding="utf-8")
    if build.returncode != 0:
        return fail(f"build exit code {build.returncode}: {tail(build_log)}", log_path=log_path, build_seconds=build_seconds)
    if not marker.is_file():
        return fail(f"missing success marker; Blender may have hidden a Python exception: {tail(build_log)}", log_path=log_path, build_seconds=build_seconds)
    try:
        build_result = json.loads(marker.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return fail(f"invalid success marker: {exc}", log_path=log_path, build_seconds=build_seconds)
    if not build_result.get("ok"):
        return fail("build marker did not report ok", log_path=log_path, build_seconds=build_seconds)
    if not blend.is_file() or blend.stat().st_mtime < start_wall - 2.0:
        return fail("fresh blend file was not produced", log_path=log_path, build_seconds=build_seconds)

    inspect_command = [str(blender), "--background", str(blend), "--python", str(HERE / "inspect_blend.py"), "--", str(inspection)]
    if spec:
        inspect_command.append(str(spec))
    try:
        verify, verify_seconds = run_process(inspect_command, env=env, timeout=args.timeout)
    except subprocess.TimeoutExpired as exc:
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write("\n=== VERIFY TIMEOUT ===\n" + (exc.stdout or "") + "\n" + (exc.stderr or ""))
        return fail("verification timeout", log_path=log_path, build_seconds=build_seconds)
    verify_log = verify.stdout + "\n" + verify.stderr
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write("\n=== VERIFY ===\n" + verify_log)
    if not inspection.is_file():
        return fail(f"inspection file missing: {tail(verify_log)}", log_path=log_path, build_seconds=build_seconds, verify_seconds=verify_seconds)
    inspection_result = json.loads(inspection.read_text(encoding="utf-8-sig"))
    if verify.returncode != 0 or not inspection_result.get("ok"):
        failed = [item for item in inspection_result.get("checks", []) if not item.get("pass")]
        return fail(f"inspection failed: {json.dumps(failed, ensure_ascii=False)}", log_path=log_path, build_seconds=build_seconds, verify_seconds=verify_seconds)

    payload = {
        "ok": True,
        "blend": str(blend),
        "build_seconds": round(build_seconds, 3),
        "verify_seconds": round(verify_seconds, 3),
        "build_metrics": build_result.get("metrics", {}),
        "inspection": inspection_result.get("summary", {}),
        "checks": len(inspection_result.get("checks", [])),
        "log": str(log_path),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
