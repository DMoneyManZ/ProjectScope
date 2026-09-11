# Install ProjectScope

[Home](../README.md) · [User guide](USER-GUIDE.md) · [Development](DEVELOPMENT.md)

ProjectScope installs into your own Linux account. Its editor uses GTK4 and its
overlay runs as a GNOME Shell extension. The runnable installer includes the
application source, not a bundled desktop or Python runtime.

## Check compatibility first

| Requirement | Supported target |
|---|---|
| Desktop | GNOME Shell **50** |
| Session | Wayland |
| Python | Python **3.10 or newer**, with system GTK bindings |
| Editor libraries | PyGObject, GTK4, Pycairo |
| Desktop tools | `glib-compile-schemas`, `gnome-extensions`, `gnome-shell` |

Run these from a terminal inside your GNOME desktop session:

```bash
gnome-shell --version
printf '%s\n' "$XDG_SESSION_TYPE"
python3 --version
```

This release supports GNOME 50 only. It does not support GNOME 46, KDE, other
desktop environments, Windows, or macOS. Ubuntu 24.04 is not a supported target
merely because it is Ubuntu; check the desktop version above. Do not bypass the
GNOME version check to install on an unsupported shell.

## Install system dependencies

On an Ubuntu or Debian-based system **already running GNOME Shell 50 on Wayland**,
the runtime packages are:

```bash
sudo apt install python3 python3-gi python3-cairo gir1.2-gtk-4.0 libglib2.0-bin
```

The runnable installer also includes an optional dependency setup command:

```bash
./ProjectScope-1.0.0-linux.run --install-dependencies
```

From a source checkout, the equivalent helper is:

```bash
bash tools/install-dependencies.sh
```

These helpers use `apt-get` and request administrator authorization through
`sudo` to update package lists and install the required libraries. They require
an internet connection and an existing GNOME 50 desktop; they do not upgrade
GNOME. Run the helper as your normal user, then repeat the dependency check and
application installation steps. Dependencies are downloaded from your configured
system repositories, not bundled for offline installation.

Use your distribution's equivalent packages elsewhere. This command supplies the
application libraries; it does not upgrade your desktop to GNOME 50. GNOME's
extension tools should be supplied by your desktop installation.

The dependency checker reports missing components without installing packages or
changing your desktop settings. System packages require your package manager;
the ProjectScope installer itself must run as your normal user, without sudo.
Use the system Python so it can find the distribution's `gi` and `cairo` modules.

## Option 1: runnable installer

1. Open the [v1.0.0 release](https://github.com/DMoneyManZ/ProjectScope/releases/tag/v1.0.0).
2. Download `ProjectScope-1.0.0-linux.run` and `SHA256SUMS` into the same folder.
3. Open a terminal in that folder and verify the download:

   ```bash
   sha256sum --check --ignore-missing SHA256SUMS
   ```

   Confirm that `ProjectScope-1.0.0-linux.run` reports `OK`. Stop if verification
   fails. `--ignore-missing` allows the source archive to remain undownloaded.

4. Make the installer executable and check dependencies:

   ```bash
   chmod +x ProjectScope-1.0.0-linux.run
   ./ProjectScope-1.0.0-linux.run --check
   ```

5. Once the required dependencies are available, run:

   ```bash
   ./ProjectScope-1.0.0-linux.run
   ```

   Read the installation summary and confirm when prompted.

6. **Save your work, log out, and log back in.** Open ProjectScope from the
   application menu, select **Enable extension** if needed, and choose a preset.
   Press **Home** to show or hide the overlay.

You can also invoke the installer with `python3 ProjectScope-1.0.0-linux.run`
without changing its executable bit.

### Inspect or extract without installing

```bash
./ProjectScope-1.0.0-linux.run --help
./ProjectScope-1.0.0-linux.run --extract ./ProjectScope-extracted
```

Choose a destination directory that does not already exist. Extraction writes
the source files there without installing the application or extension. The
`--check` option checks dependencies without installing or changing settings.

## Option 2: install from source

Download `ProjectScope-1.0.0-source.tar.gz` and `SHA256SUMS` from the
[release](https://github.com/DMoneyManZ/ProjectScope/releases/tag/v1.0.0), verify
with `sha256sum --check --ignore-missing SHA256SUMS`, and extract the archive.
Open a terminal in the extracted project folder.

Alternatively, use Git to get the release source:

```bash
git clone --branch v1.0.0 --depth 1 https://github.com/DMoneyManZ/ProjectScope.git
cd ProjectScope
```

Check dependencies and install:

```bash
python3 tools/check_dependencies.py
python3 tools/install.py
```

Run these as your normal desktop user. Log out and back in after installation.
The source installer performs the install directly; the runnable installer adds
an interactive confirmation step around it.

## What gets installed

Default paths, when `XDG_DATA_HOME` is unset:

| Location | Purpose |
|---|---|
| `~/.local/share/projectscope/app/` | Application, tools, and stock presets |
| `~/.local/share/gnome-shell/extensions/projectscope@local/` | GNOME overlay extension |
| `~/.local/share/applications/io.projectscope.Crosshair.desktop` | Application-menu and taskbar identity |
| `~/.local/share/icons/hicolor/scalable/apps/io.projectscope.Crosshair.svg` | Crosshair icon used by the running app |
| Your desktop directory / `ProjectScope.desktop` | Desktop launcher |
| `~/.local/share/projectscope/presets/` | Personal saved presets |

The installer compiles the extension's settings schema, requests extension
enablement, and registers ProjectScope's size/thickness shortcuts with GNOME.
Preferences live in GSettings. Existing personal presets and preferences are
retained when updating. A custom `XDG_DATA_HOME` changes the data locations above.

## Update

Run the new release's installer as the same user. **Log out and back in afterward**
so GNOME loads the updated extension code. Closing and reopening the editor alone
does not reload an already-running GNOME extension.

Normal edits, preset changes, and shortcut changes do not require a new login.

## Disable or uninstall

To stop the overlay, open **Position → Disable extension** in ProjectScope.

To remove the installed app, extension, and launchers:

```bash
python3 "${XDG_DATA_HOME:-$HOME/.local/share}/projectscope/app/tools/install.py" --uninstall
```

Personal presets and saved preferences are retained. ProjectScope's registered
size/thickness custom shortcuts are removed. Log out and back in if GNOME still
lists the removed extension.

## Troubleshooting

| Symptom | Next step |
|---|---|
| `No module named gi` or `cairo` | Install the system packages above and use the system Python, usually `/usr/bin/python3`. |
| Unsupported GNOME version | Check `gnome-shell --version`; this release requires GNOME 50. |
| GTK or session unavailable | Run from your GNOME Wayland desktop terminal as your own user. |
| First-install status / extension not found | Log out and back in, then reopen ProjectScope. |
| Overlay absent | Enable the extension; check visibility, opacity, monitor, and offsets. |
| Desktop launcher opens as text | If your desktop supports it, right-click and choose **Allow Launching**. |
| Extension error | Run `gnome-extensions info projectscope@local` and inspect `journalctl --user -b -o cat` for relevant errors. |

More shortcut, display, and overlay guidance is in the [user guide](USER-GUIDE.md#troubleshooting).
