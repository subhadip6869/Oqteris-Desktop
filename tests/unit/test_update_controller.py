"""Unit tests for UpdateController and version comparison utilities."""

import io
import json
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QCoreApplication

from oqteris.ui.controllers.update_controller import (
    UpdateController,
    format_bytes_size,
    format_bytes_speed,
    is_version_newer,
    parse_version_tuple,
)


@pytest.fixture(scope="session")
def qapp():
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication([])
    return app


def test_parse_version_tuple():
    assert parse_version_tuple("v1.2.0") == (1, 2, 0)
    assert parse_version_tuple("1.3.5") == (1, 3, 5)
    assert parse_version_tuple("v2.0") == (2, 0, 0)
    assert parse_version_tuple("v1.2.3-alpha") == (1, 2, 3)
    assert parse_version_tuple("v1.2.3+build456") == (1, 2, 3)


def test_is_version_newer():
    assert is_version_newer("1.3.0", "1.2.0") is True
    assert is_version_newer("v1.2.1", "1.2.0") is True
    assert is_version_newer("v2.0.0", "1.9.9") is True
    assert is_version_newer("1.2.0", "1.2.0") is False
    assert is_version_newer("v1.2.0", "1.2.0") is False
    assert is_version_newer("1.1.9", "1.2.0") is False


def test_format_bytes_size():
    assert format_bytes_size(500) == "500 B"
    assert format_bytes_size(1024 * 50) == "50.0 KB"
    assert format_bytes_size(1024 * 1024 * 45) == "45.0 MB"
    assert format_bytes_size(1024 * 1024 * 1024 * 2) == "2.00 GB"


def test_format_bytes_speed():
    assert format_bytes_speed(800) == "800 B/s"
    assert format_bytes_speed(1024 * 250) == "250.0 KB/s"
    assert format_bytes_speed(1024 * 1024 * 2.5) == "2.5 MB/s"


def test_update_controller_initial_state(qapp):
    controller = UpdateController()
    assert controller.status == "idle"
    assert controller.currentVersion == "1.2.1"
    assert controller.latestVersion == ""
    assert controller.downloadProgress == 0.0


def test_update_controller_check_available(qapp):
    controller = UpdateController()
    fake_release = {
        "tag_name": "v1.3.0",
        "name": "Oqteris v1.3.0 Release",
        "body": "Exciting new features and updates.",
        "published_at": "2026-11-19T00:00:00Z",
        "html_url": "https://github.com/subhadip6869/Oqteris-Desktop/releases/tag/v1.3.0",
        "assets": [
            {
                "name": "Oqteris-Setup-v1.3.0.exe",
                "browser_download_url": "https://example.com/download/Oqteris.exe",
                "size": 52428800,
            }
        ],
    }

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(fake_release).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        controller._check_worker()

    assert controller.status == "available"
    assert controller.latestVersion == "1.3.0"
    assert controller.releaseTitle == "Oqteris v1.3.0 Release"
    assert controller.assetName == "Oqteris-Setup-v1.3.0.exe"
    assert controller.assetSize == 52428800
    assert "50.0 MB" in controller.assetSizeFormatted


def test_update_controller_check_up_to_date(qapp):
    controller = UpdateController()
    fake_release = {
        "tag_name": "v1.2.1",
        "name": "Oqteris v1.2.1",
        "body": "Current version",
        "published_at": "2026-11-18T00:00:00Z",
        "html_url": "https://github.com/subhadip6869/Oqteris-Desktop/releases/tag/v1.2.1",
        "assets": [],
    }

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(fake_release).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        controller._check_worker()

    assert controller.status == "up_to_date"
