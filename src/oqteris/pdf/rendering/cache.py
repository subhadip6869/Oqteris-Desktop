"""Thread-safe LRU rendering cache for rasterized PDF pages with byte size accounting."""

from __future__ import annotations

import collections
import logging
import threading
from typing import Any, Optional

from PySide6.QtGui import QImage

logger = logging.getLogger(__name__)


class RenderCacheEntry:
    def __init__(self, key: tuple, image: QImage, size_bytes: int) -> None:
        self.key = key
        self.image = image
        self.size_bytes = size_bytes


class PageRenderCache:
    """Bounded LRU cache for rendered QImage pages."""

    def __init__(self, max_items: int = 50, max_memory_mb: int = 256) -> None:
        self._max_items = max_items
        self._max_bytes = max_memory_mb * 1024 * 1024
        self._current_bytes = 0
        self._cache: collections.OrderedDict[tuple, RenderCacheEntry] = collections.OrderedDict()
        self._lock = threading.Lock()

    def get(self, doc_id: str, page_index: int, zoom: float, rotation: int) -> Optional[QImage]:
        # Normalize zoom to 2 decimal places to increase cache hit rate
        key = (doc_id, page_index, round(zoom, 2), rotation % 360)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key].image
        return None

    def put(self, doc_id: str, page_index: int, zoom: float, rotation: int, image: QImage) -> None:
        key = (doc_id, page_index, round(zoom, 2), rotation % 360)
        size_bytes = image.sizeInBytes()

        with self._lock:
            if key in self._cache:
                self._current_bytes -= self._cache[key].size_bytes
                del self._cache[key]

            # Evict until within limits
            while (
                len(self._cache) >= self._max_items
                or (self._current_bytes + size_bytes > self._max_bytes and self._cache)
            ):
                _, old_entry = self._cache.popitem(last=False)
                self._current_bytes -= old_entry.size_bytes

            self._cache[key] = RenderCacheEntry(key, image, size_bytes)
            self._current_bytes += size_bytes

    def invalidate_page(self, doc_id: str, page_index: int) -> None:
        """Evict all cached entries for a specific page."""
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if k[0] == doc_id and k[1] == page_index
            ]
            for k in keys_to_delete:
                entry = self._cache.pop(k)
                self._current_bytes -= entry.size_bytes

    def invalidate_document(self, doc_id: str) -> None:
        """Evict all cached entries for a document."""
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if k[0] == doc_id
            ]
            for k in keys_to_delete:
                entry = self._cache.pop(k)
                self._current_bytes -= entry.size_bytes

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._current_bytes = 0

    @property
    def memory_usage_mb(self) -> float:
        with self._lock:
            return round(self._current_bytes / (1024 * 1024), 2)

    @property
    def item_count(self) -> int:
        with self._lock:
            return len(self._cache)
