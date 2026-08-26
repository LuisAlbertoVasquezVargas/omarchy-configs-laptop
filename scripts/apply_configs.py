#!/usr/bin/env python3

import argparse
from pathlib import Path

from config_manager import (
    ConfigError,
    ERROR_STATUSES,
    compare_configs,
    comparison_diff,
    deploy,
    load_specs,
    repository_root,
    rollback,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely deploy the allowlisted Omarchy configs.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true", help="Apply the previewed changes")
    action.add_argument(
        "--rollback",
        metavar="TRANSACTION_ID",
        help="Restore a previous deployment backup",
    )
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home directory to update")
    parser.add_argument(
        "--skip-live-validation",
        action="store_true",
        help="Skip Hyprland reload/state checks (syntax validation still runs)",
    )
    parser.add_argument("--max-diff-lines", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.rollback:
        try:
            warnings = rollback(args.home, args.rollback, skip_live=args.skip_live_validation)
        except ConfigError as error:
            print(f"error: {error}")
            return 2
        print(f"Rolled back transaction {args.rollback}")
        for warning in warnings:
            print(f"warning: {warning}")
        return 0

    repo_root = repository_root()
    try:
        specs = load_specs(repo_root)
        comparisons = compare_configs(repo_root, args.home, specs)
    except ConfigError as error:
        print(f"error: {error}")
        return 2

    print("Deployment preview")
    print(f"Source: {repo_root / '.config'}")
    print(f"Target: {args.home / '.config'}")
    print()
    for comparison in comparisons:
        print(f"[{comparison.status}] {comparison.spec.path}")
        for line in comparison_diff(comparison, args.max_diff_lines):
            print(f"  {line}")

    if any(comparison.status in ERROR_STATUSES for comparison in comparisons):
        print("\nRefusing deployment because an unsafe target was found.")
        return 2

    if all(comparison.status == "match" for comparison in comparisons):
        print("\nAll managed configs already match.")
        return 0

    if not args.apply:
        print("\nDry run only. Re-run with --apply to deploy these changes.")
        return 1

    try:
        result = deploy(
            repo_root,
            args.home,
            specs,
            skip_live=args.skip_live_validation,
        )
    except ConfigError as error:
        print(f"error: {error}")
        return 2

    print(f"\nDeployment complete. Backup transaction: {result.transaction_id}")
    for warning in result.warnings:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
