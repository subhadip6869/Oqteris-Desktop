"""Unit tests for settings management and atomic persistence."""

from pathlib import Path
from oqteris.config.settings import SettingsManager


def test_settings_default_values(test_settings: SettingsManager):
    assert test_settings.get("theme") in ("light", "dark", "system")
    assert test_settings.get("default_zoom") == 1.0
    assert test_settings.get("autosave_enabled") is True
    assert test_settings.get("recent_files_limit") == 20


def test_settings_update_and_atomic_save(test_settings: SettingsManager, temp_dir: Path):
    test_settings.set("default_author", "Subhadip Dutta")
    test_settings.set("theme", "dark")
    test_settings.set("autosave_interval_seconds", 120)

    # Re-read from disk in new instance to verify atomic write
    new_settings = SettingsManager(file_path=test_settings._file_path)
    assert new_settings.get("default_author") == "Subhadip Dutta"
    assert new_settings.get("theme") == "dark"
    assert new_settings.get("autosave_interval_seconds") == 120
