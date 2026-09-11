# Contributing to ProjectScope

Thanks for helping improve ProjectScope. Start with the [development guide](docs/DEVELOPMENT.md)
for setup, architecture, and checks.

## Report a bug

Open an [issue](https://github.com/DMoneyManZ/ProjectScope/issues) with:

- Your ProjectScope release and installation method.
- Distribution, `gnome-shell --version`, Python version, and session type.
- Steps to reproduce, what you expected, and what happened.
- Display scaling and monitor layout if positioning or rendering is involved.
- Relevant ProjectScope errors from `gnome-extensions info projectscope@local`
  or the user journal.

Include a screenshot or minimal preset JSON when it helps explain the problem.
Remove personal information from logs and screenshots before sharing them. For
shortcut issues, include the binding and whether the problem happens with the
editor closed.

This release targets GNOME Shell 50 on Wayland. If you are experimenting with
another desktop version, identify it clearly rather than assuming compatibility.

## Propose a change

For a larger feature or another desktop backend, open an issue first to discuss
the behavior and scope. Focused bug fixes, documentation corrections, and preset
improvements can go directly to a pull request.

Keep each pull request focused. Explain the user-visible problem, what changes,
and which checks you ran. Add a screenshot for visual changes and describe any
manual verification that still needs to happen. Do not include personal settings,
generated build output, or local session logs.

## Validate your work

Run the checks relevant to your change from [Development](docs/DEVELOPMENT.md#run-checks).
For profile or preset changes, run the shared preset validator. For rendering,
shortcut, or lifecycle changes, exercise both the appropriate automated checks
and the isolated GNOME session when your environment supports it. State any
checks you could not run and why.

Preserve these behaviors:

- Invalid profiles never replace the last valid active design.
- Personal presets remain separate from stock presets.
- The overlay stays click-through and cleans up its drawing and bindings.
- Python and GJS agree on supported geometry and profile bounds.
- Installation and removal affect ProjectScope-owned files and settings.

Describe compatibility and performance only as far as your evidence supports.
Do not imply game approval or anti-cheat guarantees from renderer or desktop tests.

## License

ProjectScope is distributed under [GNU GPL version 3](LICENSE) (`GPL-3.0-only`). Contributions
should be compatible with that license; credit third-party work and preserve
its required notices.
