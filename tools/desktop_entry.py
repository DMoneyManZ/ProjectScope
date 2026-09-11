"""Register the same application identity for GTK, GNOME Shell and the icon theme."""
import shutil

APP_ID = 'io.projectscope.Crosshair'


def quoted(path):
    return '"' + str(path).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'


def install_launchers(app, data, desktop, executable):
    icon = data / 'icons/hicolor/scalable/apps' / (APP_ID + '.svg')
    icon.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app / 'assets/projectscope.svg', icon)
    body = '\n'.join([
        '[Desktop Entry]', 'Type=Application', 'Version=1.0', 'Name=ProjectScope',
        'Comment=Customize your crosshair · Home toggles visibility',
        f'Exec={quoted(executable)} {quoted(app / "launch.py")}',
        'Icon=' + APP_ID, 'StartupWMClass=' + APP_ID,
        'Terminal=false', 'Categories=Utility;Game;', 'StartupNotify=true', ''])
    launcher = data / 'applications' / (APP_ID + '.desktop')
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(body)
    # Keep old pinned shortcuts usable, without creating a duplicate application-menu entry.
    legacy = data / 'applications/projectscope.desktop'
    if legacy.exists():
        legacy.write_text(body + 'NoDisplay=true\n')
    desktop.mkdir(parents=True, exist_ok=True)
    shortcut = desktop / 'ProjectScope.desktop'
    shortcut.write_text(body); shortcut.chmod(0o755)
    return launcher, shortcut
