#!/bin/sh
set -eu

ROOT="${1:-$HOME/Documents/ipad-capability-sources}"
mkdir -p "$ROOT"
cd "$ROOT"

sync_repo() {
  name="$1"
  url="$2"
  branch="$3"
  if [ -d "$name/.git" ]; then
    echo "[update] $name"
    git -C "$name" fetch --depth 1 origin "$branch"
    git -C "$name" reset --hard "origin/$branch"
  else
    echo "[clone]  $name"
    git clone --depth 1 --branch "$branch" "$url" "$name"
  fi
}

sync_repo a-shell https://github.com/holzschu/a-shell.git master
sync_repo ish https://github.com/ish-app/ish.git master
sync_repo codeapp https://github.com/thebaselab/codeapp.git main
sync_repo code-server https://github.com/coder/code-server.git main
sync_repo UTM https://github.com/utmapp/UTM.git main
sync_repo SideStore https://github.com/SideStore/SideStore.git develop
sync_repo LiveContainer https://github.com/LiveContainer/LiveContainer.git main

echo "Capability source checkout is ready at: $ROOT"
