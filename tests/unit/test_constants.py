"""Unit tests verifying application metadata, organization, and constants."""

from oqteris.core.constants import (
    APP_IDENTIFIER,
    APP_NAME,
    APP_VERSION,
    DEVELOPER_GITHUB_USERNAME,
    DEVELOPER_NAME,
    ORGANIZATION_NAME,
    ORGANIZATION_URL,
    REPOSITORY_NAME,
    REPOSITORY_URL,
    get_assets_dir,
)


def test_application_metadata():
    assert APP_NAME == "Oqteris"
    assert APP_VERSION == "1.2.0"
    assert APP_IDENTIFIER == "app.vercel.originsd.oqteris"
    assert ORGANIZATION_NAME == "OriginSD"
    assert ORGANIZATION_URL == "https://originsd.vercel.app"
    assert DEVELOPER_NAME == "Subhadip Dutta"
    assert DEVELOPER_GITHUB_USERNAME == "subhadip6869"
    assert REPOSITORY_NAME == "Oqteris-Desktop"
    assert REPOSITORY_URL == "https://github.com/subhadip6869/Oqteris-Desktop"


def test_get_assets_dir():
    assets = get_assets_dir()
    assert assets.is_dir()
    assert (assets / "icons" / "ui").is_dir()
    assert (assets / "icons" / "app").is_dir()
    assert (assets / "icons" / "ui" / "zoom-in.svg").is_file()
