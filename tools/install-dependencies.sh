#!/bin/bash
# Install system libraries only; application installation remains per-user.
set -euo pipefail
version=$(gnome-shell --version 2>/dev/null || true)
case "$version" in
  'GNOME Shell 50'|'GNOME Shell 50.'*) ;;
  *) printf '%s\n' 'ProjectScope requires an existing GNOME Shell 50 desktop. No packages changed.' >&2; exit 1 ;;
esac
if ! command -v apt-get >/dev/null; then
  printf '%s\n' 'Automatic dependency installation supports Ubuntu/Debian apt only. See docs/INSTALL.md.' >&2
  exit 1
fi
printf '%s\n' 'Install Python, PyGObject, Pycairo, GTK 4 introspection, and GLib tools from your system repositories.'
if [ "$EUID" -eq 0 ]; then
  apt-get update
  apt-get install python3 python3-gi python3-cairo gir1.2-gtk-4.0 libglib2.0-bin
else
  sudo apt-get update
  sudo apt-get install python3 python3-gi python3-cairo gir1.2-gtk-4.0 libglib2.0-bin
fi
