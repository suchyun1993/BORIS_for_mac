# BORIS_for_Mac Release Notes

## Build Standalone App

```bash
/Users/yun/Codex_projects/BORIS-stable-external/scripts/build_boris_for_mac_app.sh 2.0.0
```

Output app:

`/Users/yun/Codex_projects/dist/BORIS_for_Mac.app`

## Build DMG

```bash
/Users/yun/Codex_projects/BORIS-stable-external/scripts/build_boris_for_mac_dmg.sh 2.0.0
```

Output DMG:

`/Users/yun/Codex_projects/dist/BORIS_for_Mac-2.0.0-arm64.dmg`

## Update Homebrew Cask Template

```bash
/Users/yun/Codex_projects/BORIS-stable-external/scripts/update_homebrew_cask.sh 2.0.0 yourname BORIS_for_Mac
# or
/Users/yun/Codex_projects/BORIS-stable-external/scripts/update_homebrew_cask.sh 2.0.0 yourname/BORIS_for_Mac
```

Output cask:

`/Users/yun/Codex_projects/homebrew-boris-for-mac/Casks/boris-for-mac.rb`

## Publish

1. Upload the DMG asset to GitHub Release tag `v2.0.0`.
2. Push the tap repo with the updated cask.
3. Users install via:

```bash
brew tap yourname/boris-for-mac
brew install --cask boris-for-mac
```
