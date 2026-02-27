#!/usr/bin/env bash
set -euo pipefail

# Sync local `develop` branch content to the standalone dev preview repo
# Repo: ogradyliam5/microsoftagenticaiweekly-dev (published via GitHub Pages from main)

SRC_REPO="/home/liam_vm/.openclaw/workspace/microsoftagenticaiweekly"
DEV_REMOTE_URL="https://github.com/ogradyliam5/microsoftagenticaiweekly-dev.git"

cd "$SRC_REPO"

current_branch="$(git rev-parse --abbrev-ref HEAD)"
trap 'git checkout "$current_branch" >/dev/null 2>&1 || true' EXIT

git checkout develop >/dev/null 2>&1

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"; git checkout "$current_branch" >/dev/null 2>&1 || true' EXIT

git clone "$SRC_REPO" "$tmpdir/site" >/dev/null 2>&1
cd "$tmpdir/site"
git checkout develop >/dev/null 2>&1

git remote add dev "$DEV_REMOTE_URL"
git push -f dev develop:main

echo "Dev preview synced: https://ogradyliam5.github.io/microsoftagenticaiweekly-dev/"