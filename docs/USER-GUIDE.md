# ProjectScope user guide

[Home](../README.md) · [Installation](INSTALL.md) · [Development](DEVELOPMENT.md)

A native crosshair editor and GNOME desktop overlay. Press **Home** to show or
hide the crosshair. Closing the editor leaves the extension running.

## First use

1. Open **ProjectScope** from your Desktop or Ubuntu's application menu.
2. If it reports “First install”, save your work, log out of Ubuntu and log back
   in once. GNOME discovers the new extension when the session starts.
3. Reopen ProjectScope. Select **Enable extension** if its status is off.
4. Choose a preset on the left. Edits to the controls apply immediately.
5. Press **Home** on the desktop or in a game to show/hide the crosshair.
   The visible switch in the editor reflects the same saved state.
6. Close the editor. Your crosshair remains available and your last visibility
   choice is restored on the next login. There is no background editor to keep open.

Home is reserved globally while the extension is enabled. If you need Home for
another application, choose **Ctrl + Home** or **F8** in **Settings**.
This is a toggle, not hold-to-show. Keyboard repeat is ignored. The shortcut is
inactive on the lock screen; the crosshair also hides in the Activities overview.

## Cycle crosshairs while playing

Press **Page Up** for the previous saved preset or **Page Down** for the next.
Cycling wraps at either end in sidebar order and works with the editor closed.
Home still toggles visibility; cycling a hidden crosshair leaves it hidden.

Use **Save as preset** before cycling to keep your edits. Imported profiles join
the cycle after saving. In **Settings**, change or disable the previous/next preset shortcuts if a game
needs those keys. Ctrl + Page Up / Page Down are already used for thickness;
reassign those actions first if you want to use that combination for cycling.
After manually copying JSON files into the presets folder, reopen the editor to
refresh the library. No background polling is used.

## Keyboard controls and random designs

| Default key | Action |
|---|---|
| Home | Show/hide crosshair |
| Page Up / Page Down | Previous/next saved preset |
| Ctrl + Page Up / Page Down | Increase/decrease thickness by 0.25; dot radius for dots |
| Shift + Page Up / Page Down | Increase/decrease overall scale by 0.25×, within 0.25×–8.0× |
| Pause | Generate a compact random design |
| Insert | Save the current design under its current name |
| End | Next color, alternating light/dark |

Open **Settings**, click an action’s shortcut, and press your new keys. Escape
cancels; Backspace disables that action. Duplicate ProjectScope bindings are
rejected. **Restore default shortcuts** resets every action to the table above.
Changes apply immediately and persist across logins.

These shortcuts are global. Check your desktop and game's keyboard settings for
conflicts; ProjectScope does not inspect or alter game bindings. Delete is unused
by default. Size and thickness shortcuts work with the editor closed; save the
preset to retain changes when cycling away from it.

**OG controls** in Settings enables the original Home-only controls and turns off
labels and inversion. Size and thickness shortcuts pause in this mode. Turning OG
controls off restores your previous controls and display options. This is a
reversible settings mode; it does not change your crosshair or downgrade software.

Randomize chooses a compact dot, cross or ring with bounded geometry. It keeps
opacity and visibility, including zero opacity or a hidden crosshair. It does not
analyze the game. Edit results you like and save before generating another.

Insert works with the editor closed. It runs a short-lived local save helper,
then updates the cycling library. **Saving the same name replaces your personal
copy**; rename first if you want separate shape variants. Stock files are retained.
No terminal is opened. A failed save is reported in the corner label when enabled.

End cycles 12 colors in alternating light/dark pairs. It preserves shape and
opacity and picks an opposite outline color. It switches off crosshair inversion
so the selected color is visible. Save to keep a color change in the preset.

## Weapon-style presets and fading label

There are **30 stock presets**, including six each for **Sniper, SMG, Shotgun and
Pistol**. See the [preset guide](../support/PRESET-GUIDE.md) and
[preset gallery](../support/preset-gallery.png).
These are visual options, not weapon detection, spread simulation or accuracy
predictions. Page Up/Down follows sidebar order.

Switching presets, randomizing, cycling color or saving shows a small label at
the upper-right of the chosen monitor. It stays for about 1.8 seconds, then fades
over 1.2 seconds. It displays the preset name and saved RGB values on a 0–255 scale.
Toggle **Fading preset label** off to disable it.

## Transparency and inversion

Opacity **0.4–0.6** gives an ordinary see-through crosshair. The background affects
its apparent color naturally through alpha blending.

**Invert label against background** is on by default. White text becomes dark
over light backgrounds and light over dark backgrounds through GPU destination
color blending. Disable it for white lettering with a black outline.

**Invert crosshair against background** is optional and off by default. It uses
a white silhouette of your geometry as an inversion mask, respecting opacity.
Your stored color and outline stay saved but do not define that inverted
silhouette. The editor preview displays your stored design in ordinary color.
End returns to ordinary color mode.

These effects contain no screenshot capture, framebuffer readback, player
recognition or game-memory access. The GPU combines the overlay texture with
the existing desktop framebuffer. Inversion can have weak contrast near middle
gray; it is not a guarantee of readability on every background. The small effect
texture and brief label animation add compositor work; no zero-cost claim is made.

## Customize

The preview shows dark and lighter backgrounds. Dimensions are desktop logical
pixels, so display scaling can change the corresponding number of physical pixels.

- **Cross lines:** enable arms, remove the top arm, adjust length/thickness/gap.
- **Center dot:** enable and set radius.
- **Circle:** enable and set radius and thickness.
- **Crosshair/outline colors:** choose any color using the native color chooser.
- **Outline width:** black by default, adjustable or disabled at zero.
- **Opacity:** applies to the entire crosshair; zero makes it invisible.
- **Overall scale:** multiplies every dimension, including outlines.
- **Rotation:** turns the geometry around the center.

Keep at least one component enabled. An invalid edit displays a message and leaves
last valid overlay settings intact. Changes are remembered automatically; **Save as
preset** adds them to your named library. Rename before saving to retain separate
variants. Saving the same normalized name replaces your custom copy. Stock files
are never overwritten. **Reset to selected preset** restores the selected saved
profile (or the stock CS2 preset if nothing is selected).

## Presets

| Preset | Visual purpose | Tradeoff |
| --- | --- | --- |
| CS2 Precision | Compact cyan cross | Gap preserves the central view |
| DayZ Small Dot | Small outlined white dot | Little obstruction, less noticeable |
| Bodycam Subtle Dot | White dot at reduced opacity | Can disappear against bright scenes |
| FPS Balanced | Green cross and dot | More central detail is covered |
| High Contrast | Yellow cross with heavier outline | More visible, larger footprint |
| FPS Ring | Cyan ring and center dot | Ring covers more surrounding detail |

These are editable starting points. A fixed screen-center mark does not track
weapon sway, recoil, aiming-down-sights alignment, or bullet impact.

## Import, export, and moving to another computer

Use **Export preset…** to save the current geometry as a JSON file. Use **Import
preset…** to validate and apply a ProjectScope JSON file; then **Save as preset**
to add it to your library. Malformed or oversized imports do not replace the
active preset. Each file contains one profile, not a list or executable script.

Version 1 supports lines, dots and circles. Crosshair X's proprietary preset files
and custom PNG/image overlays are not supported in this release. ProjectScope
JSON is portable and intended for the future Windows backend; a working Windows
Game Bar application is not included in this Ubuntu release.

## Position and monitors

Choose Primary display or a numbered monitor in **Position**. Adjust
horizontal/vertical offsets to align with a game viewport. Centering uses the
whole monitor, not automatic game-window detection. Use a centered fullscreen or
borderless game viewport. If the selected monitor is absent, the primary display
is used. Monitor numbers can change when displays are reconnected.

## Compatibility and resource use

This release targets **GNOME Shell 50 on Wayland**, with Ubuntu-oriented installation guidance. It draws
through GNOME, independently of game processes. It does not read game memory,
inject code, hook game rendering, automate input, or change anti-cheat settings.
It cannot guarantee a game permits crosshair overlays or that no kick/ban will
occur. Game/server rules still apply. Crosshair X's Windows Game Bar mechanism
is not available on Ubuntu, and its compatibility claims do not transfer here.

The crosshair geometry is static, with no game scanning. Settings/display changes
request repainting; the corner label briefly animates during its fade. GNOME still composites the overlay,
which can affect direct scanout and frame timing. Performance in your games must
be measured on your setup; no zero-impact or ban-free promise is made.

## Troubleshooting

- **No crosshair:** check extension status, Show crosshair, opacity, display choice
  and offsets. Log out/in after first installation. Home works only while the
  extension is active. Some keyboard layouts require Fn + Home.
- **Home conflicts:** select Ctrl + Home or F8. Another global binding may prevent
  a shortcut from registering; check Ubuntu keyboard shortcuts if it still fails.
- **Extension error:** run `gnome-extensions info projectscope@local`, and inspect
  `journalctl --user -b -o cat` for ProjectScope errors. Use the Enable button only
  after correcting an error or updating. Shell updates may require a new version.
- **Windowed game:** the crosshair remains at monitor center; manually offset it
  or use borderless/fullscreen. There is no game-window tracking.
- **Overlay blocked:** do not disable or bypass game protection to make it appear.
- **Desktop shortcut opens as text:** right-click it and select Allow Launching.

## Installation, updates, and removal

See the [installation guide](INSTALL.md) for the runnable installer, dependency
packages, source installation, updates, and removal. Log out and back in after
installation or an extension update. Normal use and changing presets require no
logout.

Use **Disable extension** in **Position** to stop drawing and release the overlay's
shortcuts. The uninstaller removes the app, extension, and launchers while
retaining personal presets and saved preferences.

For source checks and isolated desktop tests, see [Development](DEVELOPMENT.md).
