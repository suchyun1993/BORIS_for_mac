# BORIS_for_Mac

`BORIS_for_Mac` is an ARM-based macOS-focused build derived from [BORIS](https://github.com/olivierfriard/BORIS) (Behavioral Observation Research Interactive Software).

This repository keeps the BORIS core workflow, and adds a mac-oriented embedded playback path, packaging scripts, and Homebrew cask release tooling.

## Upstream Relationship

- Upstream project: `olivierfriard/BORIS`
- This project: customized macOS variant for your workflow and deployment
- Base code copyright remains with original BORIS authors where indicated in source headers

This is **not** an official BORIS release. It is a maintained downstream variant.

## What Is Different Here

- macOS-specific launch profile (`BORIS_for_Mac`) and separate config paths
- embedded player path tuned for current mac usage
- standalone app packaging via PyInstaller
- Several new shortcuts for easily tuning video player
- Homebrew tap/cask update helper scripts

## Repository Layout

- `src/boris/`: BORIS application source (including local modifications)
- `launch.command`: local source-run launcher profile
- `packaging/pyinstaller/`: standalone app build entry/spec/runtime hooks
- `scripts/build_boris_for_mac_app.sh`: build `.app`
- `scripts/build_boris_for_mac_dmg.sh`: build `.dmg`
- `scripts/update_homebrew_cask.sh`: update cask metadata from local DMG

## Run From Source (local dev)

```bash
./launch.command
```

## Build Standalone App + DMG

```bash
./scripts/build_boris_for_mac_app.sh 2.0.0
./scripts/build_boris_for_mac_dmg.sh 2.0.0
```

Output example:

- `/Users/yun/Codex_projects/dist/BORIS_for_Mac.app`
- `/Users/yun/Codex_projects/dist/BORIS_for_Mac-2.0.0-arm64.dmg`

## Homebrew (Tap + Cask)

User install:

```bash
brew tap <github_user>/boris-for-mac
brew install --cask boris-for-mac
```

Maintainer cask refresh:

```bash
./scripts/update_homebrew_cask.sh 2.0.0 <github_user> <github_repo>
# or
./scripts/update_homebrew_cask.sh 2.0.0 <github_user>/<github_repo>
```


## License & Copyright Notes

This repository is a derivative of BORIS and should be distributed under GPL-compatible terms consistent with upstream headers (BORIS source files indicate GNU GPL v3 or later).

When publishing:

- keep original copyright/license headers in source files
- clearly state it is a downstream/custom variant of BORIS
- keep attribution to upstream BORIS and its author(s)
- when shipping binaries (`.app`/`.dmg`), provide corresponding source code for that exact release tag
- preserve notices for bundled third-party components and comply with their licenses

If you want stricter release hygiene, add a top-level `LICENSE` file (GPL-3.0-or-later text) and a `THIRD_PARTY_NOTICES.md`.

## Fork Strategy

Two valid options:

- **Option A (recommended): fork upstream BORIS**
  - best traceability to upstream history
  - easy to show your delta in PR-like form
- **Option B: independent repository**
  - keep `upstream` remote pointing to original BORIS
  - manually sync upstream changes as needed

For GPL-derived maintenance, either option works as long as source and notices are properly provided.
