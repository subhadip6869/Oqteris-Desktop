# Release and Deployment Process

Oqteris utilizes automated GitHub Actions pipelines to build, test, package, and publish releases.

## Versioning Scheme

Oqteris adheres to [Semantic Versioning 2.0.0](https://semver.org/):
`v<MAJOR>.<MINOR>.<PATCH>` (e.g. `v1.0.0`).

## Automated Release Workflow

1. **Tag Creation**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
2. **GitHub Actions Matrix**:
   - Compiles Windows standalone x64 package and Inno Setup installer.
   - Compiles macOS Apple Silicon and Intel `.app` bundles and DMGs.
   - Packages Linux Debian `.deb`, RPM `.rpm`, and Arch Linux `.pkg.tar.zst`.
3. **Artifact Verification & Integrity**:
   - Computes SHA-256 hashes for all generated release artifacts (`SHA256SUMS.txt`).
4. **GitHub Release Publication**:
   - Automatically drafts and publishes a GitHub Release for the tag.
   - Attaches platform packages, installers, and checksums.
