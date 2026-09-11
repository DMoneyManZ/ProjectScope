# Public release validation

Release: v1.0.0, GNOME Shell 50. Application release numbering is separate from extension revision 5.

Checks performed during release preparation:

- 28 Python tests, including runnable installer extraction, refusal to overwrite existing data, archive traversal rejection, dependency-installer version gating, and desktop identity/icon registration.
- GJS renderer, preset cycling, and color checks.
- 30 stock presets and 1,000 generated random profiles passed the production profile validator.
- Python byte-compilation and strict GLib schema compilation.
- Runnable installer source extraction and rebuilding from its source archive.
- Dependency checker passes on the GNOME 50.1 build host. It performs no installation or settings changes.
- Public source/artifact allowlist excludes local development tasks, old release backups, personal presets, and session logs.
- Supplied editor/overlay screenshots and generated banner visually inspected before inclusion.

The launcher uses the application's GTK ID, `io.projectscope.Crosshair`, for its desktop entry and theme icon. The icon registration test resolves the resulting desktop entry and checks the installed SVG.

These release checks do not re-establish the historical native session results recorded in [VALIDATION.md](../VALIDATION.md). No protected-game compatibility, Windows support, or offline bundled GNOME runtime is claimed. The optional dependency installer downloads distribution packages; it does not upgrade GNOME.
