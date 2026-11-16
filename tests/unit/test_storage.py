"""Unit tests for platform-aware storage and temporary file management."""

from pathlib import Path
from oqteris.platform.storage import StorageManager


def test_storage_directories_creation(temp_dir: Path):
    storage = StorageManager(app_name="TestApp", org_name="TestOrg")
    storage._data_dir = temp_dir / "data"
    storage._config_dir = temp_dir / "config"
    storage._cache_dir = temp_dir / "cache"
    storage._logs_dir = temp_dir / "logs"
    storage._temp_dir = temp_dir / "temp"
    storage._recovery_dir = temp_dir / "recovery"
    storage._backups_dir = temp_dir / "backups"
    storage._ipc_dir = temp_dir / "ipc"

    storage.ensure_directories()

    assert storage.data_dir.is_dir()
    assert storage.config_dir.is_dir()
    assert storage.cache_dir.is_dir()
    assert storage.logs_dir.is_dir()
    assert storage.temp_dir.is_dir()
    assert storage.recovery_dir.is_dir()
    assert storage.backups_dir.is_dir()
    assert storage.ipc_dir.is_dir()


def test_temporary_file_creation_and_cleanup(temp_dir: Path):
    storage = StorageManager(app_name="TestApp", org_name="TestOrg")
    storage._temp_dir = temp_dir / "temp"
    storage.ensure_directories()

    temp_file = storage.get_temporary_file(prefix="test_", suffix=".pdf")
    assert temp_file.is_file()
    assert temp_file.parent == storage.temp_dir

    storage.clean_temp_directory()
    assert not temp_file.exists()
