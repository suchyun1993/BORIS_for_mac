# BORIS_for_Mac

`BORIS_for_Mac` is a macOS-focused build derived from [BORIS](https://github.com/olivierfriard/BORIS) (Behavioral Observation Research Interactive Software).

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
- DMG build pipeline
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
/Users/yun/Codex_projects/BORIS-stable-external/launch.command
```

## Build Standalone App + DMG

```bash
/Users/yun/Codex_projects/BORIS-stable-external/scripts/build_boris_for_mac_app.sh 2.0.0
/Users/yun/Codex_projects/BORIS-stable-external/scripts/build_boris_for_mac_dmg.sh 2.0.0
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
/Users/yun/Codex_projects/BORIS-stable-external/scripts/update_homebrew_cask.sh 2.0.0 <github_user> <github_repo>
# or
/Users/yun/Codex_projects/BORIS-stable-external/scripts/update_homebrew_cask.sh 2.0.0 <github_user>/<github_repo>
```

## What To Upload To GitHub

For each release:

1. Push source code repo (this repository) with a version tag like `v2.0.0`.
2. Upload DMG asset to that GitHub Release:
   - `BORIS_for_Mac-2.0.0-arm64.dmg`
3. Push your tap repository (`homebrew-boris-for-mac`) with updated:
   - `Casks/boris-for-mac.rb`

Recommended to also publish SHA256 in release notes.

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

## 中文说明（简版）

- 这个仓库是基于原版 BORIS 的 mac 定制分支，不是官方发行版。
- 发布时建议：
  1. 上传完整源码（本仓库）并打 `vX.Y.Z` tag  
  2. 在 Release 上传对应 DMG  
  3. 更新并发布 Homebrew tap 的 cask  
- 版权/许可上，务必保留原作者头部声明，并按 GPL 要求提供与二进制版本对应的源码。
