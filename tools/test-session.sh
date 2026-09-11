#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
TEST_ROOT=$(mktemp -d /tmp/projectscope-session-XXXXXX)
export XDG_CONFIG_HOME="$TEST_ROOT/config"
export XDG_DATA_HOME="$TEST_ROOT/data"
export XDG_CACHE_HOME="$TEST_ROOT/cache"
export XDG_RUNTIME_DIR="$TEST_ROOT/runtime"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_DATA_HOME/gnome-shell/extensions" "$XDG_CACHE_HOME" "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
cp -r extension "$XDG_DATA_HOME/gnome-shell/extensions/projectscope@local"
cp -r tests/inspector "$XDG_DATA_HOME/gnome-shell/extensions/projectscope-test-inspector@local"
mkdir -p "$XDG_DATA_HOME/projectscope/app"
cp -r projectscope tools presets extension "$XDG_DATA_HOME/projectscope/app/"
export LIBGL_ALWAYS_SOFTWARE=1
export GSK_RENDERER=cairo
printf 'Isolated test directory: %s\n' "$TEST_ROOT"
dbus-run-session -- python3 tests/session_check.py "$TEST_ROOT"
