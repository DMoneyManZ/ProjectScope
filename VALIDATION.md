# Validation — 2026-09-10

Target: Ubuntu / GNOME Shell 50.1 / Wayland. Python 3.14 and GTK 4.22
were available on the build machine. The source requires Python 3.10+.

## Automated checks

- 13 Python unittest cases pass: strict schema, bounds, malformed JSON,
  duplicate keys, Unicode/size limits, disabled-component validation, opaque
  vs transparent rendering, failed atomic saves, preset-name collisions, and catalog precedence with malformed files.
- All 30 supplied presets pass the same production validator.
- GJS loads the renderer, rejects invalid geometry, and renders Cairo output.
  Thick, rotated, outlined arms have sufficient drawing bounds.
- Python modules compile; GLib settings schema compiles in strict mode.

## Actual native-session checks

Ran a separate headless GNOME Shell 50.1 with a 1280x900 virtual Wayland
monitor and separate D-Bus/config/data/runtime directories. The live desktop
was not replaced. This exercised real GNOME and GTK APIs, not shell mocks.

- Extension reaches ACTIVE state with no extension errors.
- GTK editor opens and renders preset thumbnails and its live preview.
- Controls update GSettings; saves create named presets; invalid edits preserve
  the last valid overlay settings; startup focus does not replace the active preset.
- Home hides and shows the crosshair while a fullscreen GTK test window is focused.
- Holding Home does not repeatedly toggle it.
- A mouse click at the crosshair position reaches the fullscreen window underneath.
- Disabling releases the Home binding; re-enabling restores one working handler.

A local-only virtual input session was used by the tests. The installed
application does not create remote-desktop sessions or simulate input.

## Preset cycling update

- GJS checks cover next/previous order, wrapping, unknown current IDs, duplicate
  and invalid entries, and empty/single-entry libraries.
- Native fullscreen tests pass with the editor closed: Page Up/Down cycle all
  stock and saved custom profiles in sidebar order, wrapping both directions.
- Held Page Down advances once; cycling preserves hidden visibility.
- Disabling cycling in settings releases the shortcut. Disabling/re-enabling the
  extension releases/restores both cycling bindings.
- GTK controls follow external profile changes, and subsequent edits retain the
  newly selected profile. The cycling settings offer default, Ctrl, and disabled.

## Randomizer update

- 1,000 deterministic generated samples pass both GJS geometry checks and the
  full Python portable-profile validator, with compact bounds and shape variety.
- Real GTK Randomize button changes the profile and synchronizes the controls.
- Isolated fullscreen tests verify Pause/F9 random bindings, held-key
  suppression, opacity/hidden-state preservation, and disabled bindings.
- Extension disable/re-enable releases/restores the random shortcut.
- No extension errors were reported by the isolated GNOME session.

## Weapon presets, labels, inversion and save/color shortcuts

- 24 new weapon-style presets pass strict validation (30 stock profiles total).
- Real compositor screenshots show a white dot on black and a black dot on white
  with inversion enabled; pixel tests also verify label contrast on both.
- The label appears on preset changes and fades away after approximately 3 seconds.
- End alternates light/dark colors without changing shape, uses an opposite
  outline and exits crosshair inversion mode so the color is visible.
- Insert saves with the editor closed and refreshes the cycling library.
- Inversion controls follow external settings changes in the GTK editor.
- Click-through passes with the overlay enabled. The virtual mouse motions must
  be separated so GNOME does not coalesce them into no movement.
- The application contains no image capture/readback or synthetic input code;
  tests/inspector contains isolated screenshot tooling only, not installed or
  invoked by the production launcher.

## Limits

No actual CS2, DayZ, Bodycam, or other protected-game test was run. No anti-cheat
approval is claimed. Multi-monitor hotplug, fractional scaling, lock/unlock,
physical keyboard layout variants, long-running performance and restart after
an actual user logout/login still require checks on the user's desktop. Session
settings and geometry are designed for these cases, but that is not test evidence.
No Windows application or executable has been built or tested in this release.
The portable JSON profile format is shared with the planned Windows implementation.
No numerical CPU, GPU, memory, or game-FPS comparison against Crosshair X is claimed.

## Reproduce

From the source directory:

    python3 -m unittest discover -s tests -v
    gjs -m tests/test_draw.js
    gjs -m tests/test_cycle.js
    gjs -m tests/test_colors.js
    gjs -m tests/test_random.js > build/random-samples.jsonl
    python3 tools/check_presets.py
    bash tools/test-session.sh

The final command starts an isolated test desktop, briefly injects test input
there, then stops it. Temporary session logs are retained in /tmp/projectscope-session-*.
The editor screenshot is saved in build/editor.png. The test script requires access
to local D-Bus sockets and GNOME's rendering devices; restricted sandboxes may block it.


## Size, thickness, and Settings tab — 2026-09-10

- 24 Python tests pass, including size clamps through 8×, old-renderer compatibility, thickness changes, hidden-state preservation, shortcut customization, and default restoration.
- GJS validation/render test accepts scale 8. The isolated GNOME test passes Settings editing/capture callback, collision rejection, preset synchronization, fullscreen click-through, and extension lifecycle checks.
- Installed size/thickness helper commands were exercised down/up against the live profile; the profile was restored exactly. Registration uses GNOME custom shortcuts and preserves unrelated bindings.
- Actual physical key capture in a game remains a user check; the automated capture test emits the GTK controller signal.
- Loaded extension version 4 is temporarily limited to 4×. Version 5 supports 8× after the next login; no live desktop/extension reload was performed for this update.
