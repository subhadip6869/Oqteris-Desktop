"""Qt Quick QQuickImageProvider implementation serving dynamically colored SVG vector icons to QML."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QByteArray, QSize
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtSvg import QSvgRenderer

from oqteris.core.constants import get_assets_dir

logger = logging.getLogger(__name__)


class IconImageProvider(QQuickImageProvider):
    """Provides dynamically themed SVG icons directly to QML Image elements.

    URI format:
    image://icon/<icon_name>/<hex_color>/<pixel_size>
    Example:
    image://icon/folder-open/1E293B/36
    """

    def __init__(self, icons_dir: Optional[Path] = None) -> None:
        super().__init__(QQuickImageProvider.ImageType.Image)
        if icons_dir is None:
            self._icons_dir = get_assets_dir() / "icons" / "ui"
        else:
            self._icons_dir = icons_dir

    def requestImage(self, id_str: str, size: QSize, requested_size: QSize) -> QImage:
        try:
            parts = id_str.split("/")
            name = parts[0]
            color_part = parts[1] if len(parts) > 1 and parts[1] else "000000"
            color_hex = ("#" + color_part) if not color_part.startswith("#") else color_part
            target_size = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else (
                requested_size.width() if requested_size.width() > 0 else 32
            )

            svg_path = self._icons_dir / f"{name}.svg"
            if not svg_path.exists():
                img = QImage(target_size, target_size, QImage.Format.Format_ARGB32_Premultiplied)
                img.fill(QColor(0, 0, 0, 0))
                return img

            svg_text = svg_path.read_text(encoding="utf-8")
            colored_svg = (
                svg_text.replace('#2563EB', color_hex)
                .replace('#000000', color_hex)
                .replace('currentColor', color_hex)
            )

            renderer = QSvgRenderer(QByteArray(colored_svg.encode("utf-8")))
            image = QImage(target_size, target_size, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(QColor(0, 0, 0, 0))
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            return image
        except Exception as e:
            logger.warning("Failed to render icon %s: %s", id_str, e)
            img = QImage(24, 24, QImage.Format.Format_ARGB32_Premultiplied)
            img.fill(QColor(0, 0, 0, 0))
            return img
