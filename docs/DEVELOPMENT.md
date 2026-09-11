# Develop ProjectScope

[Home](../README.md) · [Installation](INSTALL.md) · [User guide](USER-GUIDE.md) · [Contributing](../CONTRIBUTING.md)

ProjectScope has two cooperating parts: a Python/GTK4 editor and a JavaScript
GNOME Shell extension. They share settings through GSettings and exchange
crosshair designs as validated JSON profiles.

## Set up

Use a GNOME Shell 50 Wayland desktop with Python 3.10 or newer and the
[runtime dependencies](INSTALL.md#install-system-dependencies). The JavaScript
checks also need GJS; the isolated session checks need D-Bus tools and access to
GNOME's rendering devices. On Ubuntu/Debian, the additional packages are usually
`gjs`, `dbus-daemon`, and `python3-pil` (Pillow for screenshot checks).

```bash
git clone https://github.com/DMoneyManZ/ProjectScope.git
cd ProjectScope
python3 tools/check_dependencies.py
glib-compile-schemas --strict extension/schemas
python3 -m projectscope.app
```

Run with the system Python, which can import your distribution's `gi` and `cairo`
modules. A plain virtual environment may not expose those system packages.

Starting the source editor does not install the extension. To test the live
overlay in your own session, follow the [source installation steps](INSTALL.md#option-2-install-from-source)
and log out and back in. The installed app is a copy: changing checkout files
does not update that installed copy or reload the running extension.

The editor uses the same ProjectScope settings as an installed copy. Use the
isolated session harness below when you need independent settings and data.

## Source map

| Path | Responsibility |
|---|---|
| `projectscope/app.py` | GTK editor, controls, preview, and profile actions |
| `projectscope/profiles.py` | Strict profile parsing, bounds, and serialization |
| `projectscope/storage.py` | Personal preset storage and library ordering |
| `projectscope/render.py` | Cairo rendering for editor previews and thumbnails |
| `projectscope/settings.py` | GSettings and GNOME extension status bridge |
| `projectscope/shortcuts.py`, `resize.py`, `modes.py` | Shortcut configuration, size/thickness changes, OG controls |
| `extension/extension.js` | Overlay lifecycle, monitor placement, and global bindings |
| `extension/draw.js` | Shell-side profile validation and rendering |
| `extension/cycle.js`, `random.js`, `colors.js` | Preset cycling, random geometry, and color cycling |
| `extension/label.js`, `invert.js` | Fading label and compositor blending |
| `extension/schemas/` | GSettings schema shared by the editor and extension |
| `presets/` | 30 stock JSON designs |
| `tools/` | Installation, dependency checks, preset validation, and shortcut helpers |
| `tests/` | Python/GJS checks and isolated GNOME session tooling |
| `support/` | Preset gallery, preset guide, and example profile |

## Run checks

From the project root, compile settings and run the Python, GJS, and preset checks:

```bash
glib-compile-schemas --strict extension/schemas
python3 -m unittest discover -s tests -v
gjs -m tests/test_draw.js
gjs -m tests/test_cycle.js
gjs -m tests/test_colors.js
mkdir -p build
gjs -m tests/test_random.js > build/random-samples.jsonl
python3 tools/check_presets.py
```

The randomizer writes generated samples into `build/random-samples.jsonl` for
inspection. Keep generated output out of source changes.

For real GTK and GNOME integration checks:

```bash
bash tools/test-session.sh
```

This starts a separate headless GNOME session with its own D-Bus and XDG
config/data/runtime directories. It exercises the editor, extension lifecycle,
fullscreen overlay, shortcuts, and click-through behavior using test input in
that isolated session. It does not replace your current desktop. Restricted
sandboxes may prevent access to the local sockets or rendering devices it needs.

The harness retains logs under `/tmp/projectscope-session-*` and writes an editor
screenshot to `build/editor.png`. The screenshot/input inspector under
`tests/inspector/` belongs to the test harness; it is not production overlay code.

See [VALIDATION.md](../VALIDATION.md) for recorded results and limits. A unit-test
pass does not establish support for another GNOME release, game compatibility,
or performance on other hardware.

## Changing profiles and rendering

Profiles contain a versioned design with lines, a dot, and/or a circle. Start
with [the example profile](../support/example-profile.json). Keep Python and GJS
validation and rendering behavior consistent when changing geometry or bounds.
Invalid data must leave the last valid active design intact.

Stock preset filenames must match their profile IDs. Validate the full catalog
with `python3 tools/check_presets.py` after adding or editing a preset. Personal
presets are separate from stock source files; preserve that boundary in installer
and storage changes.

## Extension development

Extension metadata declares GNOME Shell 50 support. The extension's numeric
`version` is its GNOME revision; it is separate from the application's release
version, such as `v1.0.0`.

After installing changed extension code, log out and back in to load it. Use
`gnome-extensions info projectscope@local` to inspect status and
`journalctl --user -b -o cat` for relevant errors. Reopening the editor does not
reload GNOME Shell's loaded JavaScript.

Preserve click-through behavior, cleanup on disable, held-key suppression, and
hidden visibility when changing global actions. Keep game interaction out of the
implementation: the overlay operates through the desktop compositor.
