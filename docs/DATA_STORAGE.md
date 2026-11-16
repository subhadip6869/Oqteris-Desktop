# Application Data Storage and Persistence

Oqteris adheres to standard operating system conventions for persistent data, configuration, cache, and temporary files.

## Operating System Paths

### Windows
Root directory: `%LOCALAPPDATA%\OriginSD\Oqteris`
Example: `C:\Users\<username>\AppData\Local\OriginSD\Oqteris\`

```
Oqteris/
│
├── settings.json        # Atomic user preferences
├── oqteris.db           # SQLite database (SQLAlchemy)
├── truststore.p12       # Application certificate truststore
│
├── ipc_requests/        # IPC temporary sockets
├── recovery/            # Interrupted document recovery records
├── cache/               # Rasterized tile and thumbnail cache
├── logs/                # Rotating structured logs (oqteris.log)
├── temp/                # Processing temporary files
└── backups/             # Document backup files
```

### macOS
- Application Support: `~/Library/Application Support/OriginSD/Oqteris/`
- Caches: `~/Library/Caches/OriginSD/Oqteris/`
- Logs: `~/Library/Logs/OriginSD/Oqteris/`

### Linux (XDG Base Directory Specification)
- Configuration: `~/.config/oqteris/` (or `$XDG_CONFIG_HOME`)
- Application Data: `~/.local/share/oqteris/` (or `$XDG_DATA_HOME`)
- Cache: `~/.cache/oqteris/` (or `$XDG_CACHE_HOME`)
- State & Logs: `~/.local/state/oqteris/logs/` (or `$XDG_STATE_HOME`)

---

## Clean Break from Legacy Java Implementation

As specified in project requirements, Oqteris is a **brand-new native implementation** in Python and Qt Quick/QML.

- **No Data Migration**: Oqteris deliberately does **not** import, parse, or read legacy Java formats (`recent_files.dat`, legacy `settings.json`, or Java keystores).
- **Relational Integrity**: Recent files and bookmarks are stored natively in SQLite (`oqteris.db`) with full Unicode path support, missing file detection, and relational indexing.
- **Credential Safety**: Private keys, passwords, and signing credentials are never stored in plaintext on disk or written to log files.
