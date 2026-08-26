#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from config_manager import (
    ConfigError,
    ERROR_STATUSES,
    compare_configs,
    comparison_diff,
    load_specs,
    repository_root,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare managed repository configs with a home directory."
    )
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home directory to inspect")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--max-diff-lines", type=int, default=40)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repository_root()

    try:
        specs = load_specs(repo_root)
        comparisons = compare_configs(repo_root, args.home, specs)
    except ConfigError as error:
        print(f"error: {error}")
        return 2

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "path": str(comparison.spec.path),
                        "status": comparison.status,
                        "source": str(comparison.source),
                        "target": str(comparison.target),
                    }
                    for comparison in comparisons
                ],
                indent=2,
            )
        )
    else:
        print(f"Repository: {repo_root / '.config'}")
        print(f"System:     {args.home / '.config'}")
        print()
        for comparison in comparisons:
            print(f"[{comparison.status}] {comparison.spec.path}")
            for line in comparison_diff(comparison, args.max_diff_lines):
                print(f"  {line}")
        print()
        counts = {
            status: sum(comparison.status == status for comparison in comparisons)
            for status in ("match", "different", "missing", "wrong-type", "symlink-refused")
        }
        print("Summary: " + ", ".join(f"{status}={count}" for status, count in counts.items()))

    if any(comparison.status in ERROR_STATUSES for comparison in comparisons):
        return 2
    if any(comparison.status != "match" for comparison in comparisons):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
