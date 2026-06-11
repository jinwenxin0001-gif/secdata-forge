from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def build_manifest(
    paths: dict[str, str],
    config: dict[str, Any],
    input_path: str | Path,
    reference_path: str | Path | None = None,
) -> dict[str, Any]:
    dataset = config.get("dataset", {})
    artifacts = []
    for name, value in sorted(paths.items()):
        artifact_path = Path(value)
        if artifact_path.exists() and artifact_path.is_file():
            artifacts.append(
                {
                    "name": name,
                    "path": artifact_path.as_posix(),
                    "bytes": artifact_path.stat().st_size,
                    "sha256": sha256_file(artifact_path),
                }
            )
    return {
        "tool": "secdata-forge",
        "dataset": dataset.get("name", "dataset"),
        "task": dataset.get("task", "unknown"),
        "input": Path(input_path).as_posix(),
        "reference": Path(reference_path).as_posix() if reference_path else None,
        "artifacts": artifacts,
    }


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

