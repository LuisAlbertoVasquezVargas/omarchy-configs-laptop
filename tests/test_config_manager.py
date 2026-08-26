from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from config_manager import (  # noqa: E402
    ConfigError,
    compare_configs,
    deploy,
    load_specs,
    rollback,
)


class ConfigManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.home = self.root / "home"
        (self.repo / ".config").mkdir(parents=True)
        self.home.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def build_repo(self, files: dict[str, tuple[str, str, str]]) -> None:
        manifest = ["version = 1", ""]
        for relative_path, (contents, validator, component) in files.items():
            source = self.repo / ".config" / relative_path
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(contents, encoding="utf-8")
            manifest.extend(
                [
                    "[[files]]",
                    f'path = "{relative_path}"',
                    f'validator = "{validator}"',
                    f'component = "{component}"',
                    "",
                ]
            )
        (self.repo / "config-manifest.toml").write_text("\n".join(manifest), encoding="utf-8")

    def test_manifest_rejects_unlisted_config_files(self) -> None:
        self.build_repo({"app/config": ("managed\n", "plain", "app")})
        extra = self.repo / ".config/app/extra"
        extra.write_text("unlisted\n", encoding="utf-8")

        with self.assertRaisesRegex(ConfigError, "unlisted files"):
            load_specs(self.repo)

    def test_compare_reports_each_target_state(self) -> None:
        self.build_repo(
            {
                "app/match": ("same\n", "plain", "app"),
                "app/different": ("repo\n", "plain", "app"),
                "app/missing": ("create\n", "plain", "app"),
                "app/wrong-type": ("file\n", "plain", "app"),
                "app/symlink": ("file\n", "plain", "app"),
            }
        )
        target_root = self.home / ".config/app"
        target_root.mkdir(parents=True)
        (target_root / "match").write_text("same\n", encoding="utf-8")
        (target_root / "different").write_text("home\n", encoding="utf-8")
        (target_root / "wrong-type").mkdir()
        (target_root / "symlink").symlink_to(target_root / "match")

        comparisons = compare_configs(self.repo, self.home, load_specs(self.repo))

        self.assertEqual(
            {str(comparison.spec.path): comparison.status for comparison in comparisons},
            {
                "app/match": "match",
                "app/different": "different",
                "app/missing": "missing",
                "app/wrong-type": "wrong-type",
                "app/symlink": "symlink-refused",
            },
        )

    def test_deploy_creates_backup_and_rollback_restores_state(self) -> None:
        self.build_repo(
            {
                "app/replaced": ("new\n", "plain", "app"),
                "app/created": ("created\n", "plain", "app"),
            }
        )
        target = self.home / ".config/app/replaced"
        target.parent.mkdir(parents=True)
        target.write_text("old\n", encoding="utf-8")
        transaction_id = "20260826-150000-000001"

        result = deploy(
            self.repo,
            self.home,
            load_specs(self.repo),
            transaction_id=transaction_id,
        )

        self.assertEqual(result.transaction_id, transaction_id)
        self.assertEqual(target.read_text(encoding="utf-8"), "new\n")
        self.assertEqual(
            (self.home / ".config/app/created").read_text(encoding="utf-8"),
            "created\n",
        )
        backup = (
            self.home
            / ".local/state/omarchy-configs/backups"
            / transaction_id
            / ".config/app/replaced"
        )
        self.assertEqual(backup.read_text(encoding="utf-8"), "old\n")

        rollback(self.home, transaction_id)

        self.assertEqual(target.read_text(encoding="utf-8"), "old\n")
        self.assertFalse((self.home / ".config/app/created").exists())

    def test_rollback_refuses_to_delete_modified_created_file(self) -> None:
        self.build_repo({"app/created": ("created\n", "plain", "app")})
        transaction_id = "20260826-150000-000002"
        deploy(
            self.repo,
            self.home,
            load_specs(self.repo),
            transaction_id=transaction_id,
        )
        target = self.home / ".config/app/created"
        target.write_text("user edit\n", encoding="utf-8")

        with self.assertRaisesRegex(ConfigError, "locally modified"):
            rollback(self.home, transaction_id)

        self.assertEqual(target.read_text(encoding="utf-8"), "user edit\n")

    def test_rollback_refuses_to_overwrite_modified_replacement(self) -> None:
        self.build_repo({"app/replaced": ("new\n", "plain", "app")})
        target = self.home / ".config/app/replaced"
        target.parent.mkdir(parents=True)
        target.write_text("old\n", encoding="utf-8")
        transaction_id = "20260826-150000-000003"
        deploy(
            self.repo,
            self.home,
            load_specs(self.repo),
            transaction_id=transaction_id,
        )
        target.write_text("user edit\n", encoding="utf-8")

        with self.assertRaisesRegex(ConfigError, "locally modified"):
            rollback(self.home, transaction_id)

        self.assertEqual(target.read_text(encoding="utf-8"), "user edit\n")

    def test_failed_post_deployment_validation_rolls_back_automatically(self) -> None:
        self.build_repo(
            {
                "app/replaced": ("new\n", "plain", "app"),
                "app/created": ("created\n", "plain", "app"),
            }
        )
        replaced = self.home / ".config/app/replaced"
        replaced.parent.mkdir(parents=True)
        replaced.write_text("old\n", encoding="utf-8")

        with patch(
            "config_manager.validate_deployed_files",
            side_effect=ConfigError("validation failed"),
        ):
            with self.assertRaisesRegex(ConfigError, "was rolled back"):
                deploy(
                    self.repo,
                    self.home,
                    load_specs(self.repo),
                    transaction_id="20260826-150000-000004",
                )

        self.assertEqual(replaced.read_text(encoding="utf-8"), "old\n")
        self.assertFalse((self.home / ".config/app/created").exists())

    def test_invalid_json_is_rejected_before_deployment(self) -> None:
        self.build_repo({"app/config.json": ("{not json}\n", "json", "app")})

        with self.assertRaisesRegex(ConfigError, "Invalid JSON"):
            load_specs(self.repo)


if __name__ == "__main__":
    unittest.main()
