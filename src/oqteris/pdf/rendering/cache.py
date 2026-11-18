"""Thread-safe LRU rendering cache for rasterized PDF pages with byte size accounting.

Memory budget
-------------
Full-resolution pages  : max 8 pages  / 64 MB  – only recently viewed pages stay hot.
Thumbnail pages        : max 20 thumbs / 24 MB  – side-panel thumbnails are small.

Both limits are intentionally conservative so that scrolling through a 500-page
document never causes unbounded RAM growth.  The LRU policy ensures only the
pages closest to the current viewport stay alive.
"""

from __future__ import annotations

import collections
import gc
import logging
import threading
from typing import Optional

from PySide6.QtGui import QImage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public tunables (overridable at construction time)
# ---------------------------------------------------------------------------
_DEFAULT_PAGE_MAX_ITEMS = 8
_DEFAULT_PAGE_MAX_MB = 64
_DEFAULT_THUMB_MAX_ITEMS = 20
_DEFAULT_THUMB_MAX_MB = 24


class RenderCacheEntry:
    def __init__(self, key: tuple, image: QImage, size_bytes: int) -> None:
        self.key = key
        self.image = image
        self.size_bytes = size_bytes


class PageRenderCache:
    """Bounded LRU cache for rendered QImage pages.

    Parameters
    ----------
    max_items:
        Maximum number of distinct (doc_id, page, zoom, rotation) entries to keep.
    max_memory_mb:
        Hard upper bound on total pixel-data RAM in megabytes.
    """

    def __init__(
        self,
        max_items: int = _DEFAULT_PAGE_MAX_ITEMS,
        max_memory_mb: int = _DEFAULT_PAGE_MAX_MB,
    ) -> None:
        self._max_items = max(1, max_items)
        self._max_bytes = max(1, max_memory_mb) * 1024 * 1024
        self._current_bytes = 0
        self._cache: collections.OrderedDict[tuple, RenderCacheEntry] = collections.OrderedDict()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, doc_id: str, page_index: int, zoom: float, rotation: int) -> Optional[QImage]:
        """Return the cached QImage, or None if not present (promotes to MRU)."""
        key = (doc_id, page_index, round(zoom, 2), rotation % 360)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key].image
        return None

    def put(self, doc_id: str, page_index: int, zoom: float, rotation: int, image: QImage) -> None:
        """Insert or replace a cache entry, evicting LRU entries to stay within limits."""
        key = (doc_id, page_index, round(zoom, 2), rotation % 360)
        size_bytes = image.sizeInBytes()

        # If a single page exceeds the whole budget, skip caching to avoid
        # permanently starving the cache (e.g. a 4096×4096 page at 2× DPI).
        if size_bytes > self._max_bytes:
            logger.debug(
                "PageRenderCache: skipping oversized entry %s (%.1f MB > budget %.1f MB)",
                key,
                size_bytes / 1_048_576,
                self._max_bytes / 1_048_576,
            )
            return

        with self._lock:
            # Replace existing entry for same key
            if key in self._cache:
                self._current_bytes -= self._cache[key].size_bytes
                del self._cache[key]

            # Evict LRU entries until we fit within both item and byte limits
            while self._cache and (
                len(self._cache) >= self._max_items
                or self._current_bytes + size_bytes > self._max_bytes
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
        gc.collect()

    def invalidate_document(self, doc_id: str) -> None:
        """Evict all cached entries for a document and release memory immediately."""
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if k[0] == doc_id
            ]
            for k in keys_to_delete:
                entry = self._cache.pop(k)
                self._current_bytes -= entry.size_bytes
        gc.collect()

    def clear(self) -> None:
        """Drop every cached entry and trigger garbage collection."""
        with self._lock:
            self._cache.clear()
            self._current_bytes = 0
        gc.collect()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def memory_usage_mb(self) -> float:
        with self._lock:
            return round(self._current_bytes / (1024 * 1024), 2)

    @property
    def item_count(self) -> int:
        with self._lock:
            return len(self._cache)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PageRenderCache items={self.item_count}/{self._max_items} "
            f"mem={self.memory_usage_mb:.1f}/{self._max_bytes // 1_048_576}MB>"
        )
