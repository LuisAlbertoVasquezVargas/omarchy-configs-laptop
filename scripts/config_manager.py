from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime
from difflib import unified_diff
from filecmp import cmp
from pathlib import Path
from typing import Iterable


VALIDATORS = {"plain", "json", "lua"}
DRIFT_STATUSES = {"missing", "different"}
ERROR_STATUSES = {"wrong-type", "symlink-refused"}
TRANSACTION_PATTERN = re.compile(r"^[0-9]{8}-[0-9]{6}-[0-9]{6}$")


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class FileSpec:
    path: Path
    validator: str
    component: str


@dataclass(frozen=True)
class Comparison:
    spec: FileSpec
    source: Path
    target: Path
    status: str


@dataclass(frozen=True)
class DeploymentResult:
    transaction_id: str | None
    comparisons: list[Comparison]
    warnings: list[str]


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _safe_relative_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not raw_path or path.is_absolute() or ".." in path.parts:
        raise ConfigError(f"Unsafe manifest path: {raw_path!r}")
    return path


def _inventory(config_root: Path) -> set[Path]:
    return {
        path.relative_to(config_root)
        for path in config_root.rglob("*")
        if path.is_file() or path.is_symlink()
    }


def load_specs(repo_root: Path) -> list[FileSpec]:
    manifest_path = repo_root / "config-manifest.toml"
    config_root = repo_root / ".config"

    try:
        with manifest_path.open("rb") as manifest_file:
            manifest = tomllib.load(manifest_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"Cannot read {manifest_path}: {error}") from error

    if manifest.get("version") != 1:
        raise ConfigError("config-manifest.toml must declare version = 1")

    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise ConfigError("config-manifest.toml must contain at least one [[files]] entry")

    specs: list[FileSpec] = []
    seen: set[Path] = set()

    for entry in raw_files:
        if not isinstance(entry, dict):
            raise ConfigError("Every [[files]] entry must be a table")

        raw_path = entry.get("path")
        validator = entry.get("validator")
        component = entry.get("component")

        if not isinstance(raw_path, str):
            raise ConfigError("Every manifest entry needs a string path")
        path = _safe_relative_path(raw_path)
        if path in seen:
            raise ConfigError(f"Duplicate manifest path: {path}")
        if validator not in VALIDATORS:
            raise ConfigError(f"Unsupported validator for {path}: {validator!r}")
        if not isinstance(component, str) or not component:
            raise ConfigError(f"Missing component for {path}")

        source = config_root / path
        if source.is_symlink() or not source.is_file():
            raise ConfigError(f"Manifest source must be a regular file: {source}")

        seen.add(path)
        specs.append(FileSpec(path=path, validator=validator, component=component))

    inventory = _inventory(config_root)
    unlisted = sorted(inventory - seen)
    missing = sorted(seen - inventory)
    if unlisted or missing:
        details = []
        if unlisted:
            details.append("unlisted files: " + ", ".join(map(str, unlisted)))
        if missing:
            details.append("missing files: " + ", ".join(map(str, missing)))
        raise ConfigError("Manifest/config mismatch (" + "; ".join(details) + ")")

    validate_sources(repo_root, specs)
    return specs


def validate_file(path: Path, validator: str) -> None:
    if validator == "plain":
        return

    if validator == "json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ConfigError(f"Invalid JSON in {path}: {error}") from error
        return

    if validator == "lua":
        try:
            result = subprocess.run(
                ["luac", "-p", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise ConfigError("luac is required to validate Lua configuration") from error
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise ConfigError(f"Invalid Lua in {path}: {message}")
        return

    raise ConfigError(f"Unsupported validator: {validator}")


def validate_sources(repo_root: Path, specs: Iterable[FileSpec]) -> None:
    config_root = repo_root / ".config"
    for spec in specs:
        validate_file(config_root / spec.path, spec.validator)


def compare_configs(repo_root: Path, home: Path, specs: Iterable[FileSpec]) -> list[Comparison]:
    source_root = repo_root / ".config"
    target_root = home / ".config"
    comparisons: list[Comparison] = []

    for spec in specs:
        source = source_root / spec.path
        target = target_root / spec.path

        if target.is_symlink():
            status = "symlink-refused"
        elif not target.exists():
            status = "missing"
        elif not target.is_file():
            status = "wrong-type"
        elif cmp(source, target, shallow=False):
            status = "match"
        else:
            status = "different"

        comparisons.append(Comparison(spec, source, target, status))

    return comparisons


def comparison_diff(comparison: Comparison, max_lines: int) -> list[str]:
    if comparison.status != "different":
        return []

    try:
        source_lines = comparison.source.read_text(encoding="utf-8").splitlines(keepends=True)
        target_lines = comparison.target.read_text(encoding="utf-8").splitlines(keepends=True)
    except (OSError, UnicodeDecodeError):
        return ["Text diff unavailable for this file."]

    lines = list(
        unified_diff(
            target_lines,
            source_lines,
            fromfile=f"system/.config/{comparison.spec.path}",
            tofile=f"repo/.config/{comparison.spec.path}",
            lineterm="",
        )
    )
    rendered = [line.rstrip() for line in lines[:max_lines]]
    omitted = len(lines) - max_lines
    if omitted > 0:
        rendered.append(f"... {omitted} additional diff lines omitted")
    return rendered


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json(data: dict[str, object], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2, sort_keys=True)
            output.write("\n")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def _run_hyprctl(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["hyprctl", *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise ConfigError("hyprctl is required for live Hyprland validation") from error


def validate_live_hyprland() -> None:
    reload_result = _run_hyprctl(["reload"])
    if reload_result.returncode != 0:
        raise ConfigError(reload_result.stderr.strip() or reload_result.stdout.strip())

    errors_result = _run_hyprctl(["configerrors"])
    errors = errors_result.stdout.strip()
    if errors_result.returncode != 0 or errors:
        raise ConfigError(
            errors or errors_result.stderr.strip() or "Hyprland reported config errors"
        )

    workspace_result = _run_hyprctl(["-j", "workspaces"])
    if workspace_result.returncode != 0:
        raise ConfigError(workspace_result.stderr.strip() or "Cannot inspect Hyprland workspaces")
    try:
        workspaces = json.loads(workspace_result.stdout)
        workspace_ids = sorted(
            workspace["id"]
            for workspace in workspaces
            if isinstance(workspace.get("id"), int) and workspace["id"] > 0
        )
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ConfigError(f"Cannot parse Hyprland workspaces: {error}") from error
    if workspace_ids != list(range(1, 8)):
        raise ConfigError(f"Expected workspaces 1-7, found {workspace_ids}")

    binds_result = _run_hyprctl(["-j", "binds"])
    if binds_result.returncode != 0:
        raise ConfigError(binds_result.stderr.strip() or "Cannot inspect Hyprland bindings")
    try:
        binds = json.loads(binds_result.stdout)
    except json.JSONDecodeError as error:
        raise ConfigError(f"Cannot parse Hyprland bindings: {error}") from error
    forbidden = [
        bind.get("description")
        for bind in binds
        if re.search(r"workspace (8|9|10)$", bind.get("description") or "", re.IGNORECASE)
    ]
    if forbidden:
        raise ConfigError(f"Workspace 8-10 bindings remain: {forbidden}")


def validate_deployed_files(home: Path, specs: Iterable[FileSpec]) -> None:
    target_root = home / ".config"
    for spec in specs:
        target = target_root / spec.path
        if target.is_symlink() or not target.is_file():
            raise ConfigError(f"Deployed target is not a regular file: {target}")
        validate_file(target, spec.validator)


def _validate_live_if_available(home: Path, components: set[str], skip_live: bool) -> list[str]:
    if skip_live or "hyprland" not in components or home.resolve() != Path.home().resolve():
        return []
    if not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return ["Hyprland session not detected; live reload validation was skipped."]
    validate_live_hyprland()
    return []


def _transaction_root(home: Path, transaction_id: str) -> Path:
    if not TRANSACTION_PATTERN.fullmatch(transaction_id):
        raise ConfigError(f"Invalid transaction id: {transaction_id!r}")
    return home / ".local" / "state" / "omarchy-configs" / "backups" / transaction_id


def deploy(
    repo_root: Path,
    home: Path,
    specs: list[FileSpec],
    *,
    skip_live: bool = False,
    transaction_id: str | None = None,
) -> DeploymentResult:
    comparisons = compare_configs(repo_root, home, specs)
    unsafe = [comparison for comparison in comparisons if comparison.status in ERROR_STATUSES]
    if unsafe:
        paths = ", ".join(str(comparison.spec.path) for comparison in unsafe)
        raise ConfigError(f"Refusing unsafe deployment targets: {paths}")

    changes = [comparison for comparison in comparisons if comparison.status in DRIFT_STATUSES]
    if not changes:
        return DeploymentResult(None, comparisons, [])

    transaction_id = transaction_id or datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    transaction_root = _transaction_root(home, transaction_id)
    if transaction_root.exists():
        raise ConfigError(f"Backup transaction already exists: {transaction_root}")

    backup_root = transaction_root / ".config"
    metadata_path = transaction_root / "transaction.json"
    created: list[dict[str, str]] = []
    replaced: list[dict[str, str]] = []

    try:
        transaction_root.mkdir(parents=True)

        for comparison in changes:
            if comparison.status == "different":
                backup = backup_root / comparison.spec.path
                _atomic_copy(comparison.target, backup)
                replaced.append(
                    {
                        "path": str(comparison.spec.path),
                        "validator": comparison.spec.validator,
                        "component": comparison.spec.component,
                        "installed_sha256": _sha256(comparison.source),
                    }
                )

        for comparison in changes:
            if comparison.status == "missing":
                created.append(
                    {
                        "path": str(comparison.spec.path),
                        "validator": comparison.spec.validator,
                        "component": comparison.spec.component,
                        "installed_sha256": _sha256(comparison.source),
                    }
                )

        metadata: dict[str, object] = {
            "version": 1,
            "transaction_id": transaction_id,
            "created": created,
            "replaced": replaced,
        }
        _atomic_json(metadata, metadata_path)

        for comparison in changes:
            _atomic_copy(comparison.source, comparison.target)

        changed_specs = [comparison.spec for comparison in changes]
        validate_deployed_files(home, changed_specs)
        warnings = _validate_live_if_available(
            home,
            {spec.component for spec in changed_specs},
            skip_live,
        )
    except Exception as error:
        if metadata_path.exists():
            try:
                rollback(home, transaction_id, skip_live=True, force=True)
            except Exception as rollback_error:
                message = (
                    f"Deployment failed ({error}); automatic rollback also failed "
                    f"({rollback_error})"
                )
                raise ConfigError(message) from error
            raise ConfigError(f"Deployment failed and was rolled back: {error}") from error
        raise ConfigError(f"Deployment failed before any target was changed: {error}") from error

    return DeploymentResult(transaction_id, comparisons, warnings)


def rollback(
    home: Path,
    transaction_id: str,
    *,
    skip_live: bool = False,
    force: bool = False,
) -> list[str]:
    transaction_root = _transaction_root(home, transaction_id)
    metadata_path = transaction_root / "transaction.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConfigError(f"Cannot read rollback metadata {metadata_path}: {error}") from error

    if metadata.get("version") != 1 or metadata.get("transaction_id") != transaction_id:
        raise ConfigError(f"Invalid rollback metadata: {metadata_path}")

    created = metadata.get("created", [])
    replaced = metadata.get("replaced", [])
    if not isinstance(created, list) or not isinstance(replaced, list):
        raise ConfigError(f"Invalid rollback entries: {metadata_path}")

    target_root = home / ".config"
    components: set[str] = set()

    for entry in created:
        path = _safe_relative_path(entry["path"])
        target = target_root / path
        components.add(entry["component"])
        if not target.exists() and not target.is_symlink():
            continue
        if target.is_symlink() or not target.is_file():
            raise ConfigError(f"Refusing to remove changed deployment target: {target}")
        if not force and _sha256(target) != entry["installed_sha256"]:
            raise ConfigError(f"Refusing to remove locally modified deployment target: {target}")

    for entry in replaced:
        path = _safe_relative_path(entry["path"])
        backup = transaction_root / ".config" / path
        target = target_root / path
        components.add(entry["component"])
        if backup.is_symlink() or not backup.is_file():
            raise ConfigError(f"Missing rollback backup: {backup}")
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ConfigError(f"Refusing unsafe rollback target: {target}")
        if not force and target.is_file() and _sha256(target) != entry["installed_sha256"]:
            raise ConfigError(f"Refusing to overwrite locally modified deployment target: {target}")

    for entry in created:
        target = target_root / _safe_relative_path(entry["path"])
        if target.exists() or target.is_symlink():
            target.unlink()

    for entry in replaced:
        path = _safe_relative_path(entry["path"])
        target = target_root / path
        _atomic_copy(transaction_root / ".config" / path, target)
        validate_file(target, entry["validator"])

    return _validate_live_if_available(home, components, skip_live)
