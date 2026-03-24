# BORIS_for_Mac Release Notes

## Build Standalone App

```bash
./scripts/build_boris_for_mac_app.sh 2.0.1
```

Output app:

`/Users/yun/Codex_projects/dist/BORIS_for_Mac.app`

## Build DMG

```bash
./scripts/build_boris_for_mac_dmg.sh 2.0.1
```

Output DMG:

`/Users/yun/Codex_projects/dist/BORIS_for_Mac-2.0.1-arm64.dmg`

## Update Homebrew Cask Template

```bash
./scripts/update_homebrew_cask.sh 2.0.1 suchyun1993 BORIS_for_mac
# or
./scripts/update_homebrew_cask.sh 2.0.1 suchyun1993/BORIS_for_mac
```

Output cask:

`/Users/yun/Codex_projects/homebrew-boris-for-mac/Casks/boris-for-mac.rb`

## Publish

1. Upload the DMG asset to GitHub Release tag `v2.0.1`.
2. Push the tap repo with the updated cask.
3. Users install via:

```bash
brew tap suchyun1993/boris-for-mac
brew install --cask boris-for-mac
```
