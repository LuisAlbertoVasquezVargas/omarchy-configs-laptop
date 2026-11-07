<!-- README.md -->

# Omarchy Laptop Config

Personal configuration for Omarchy 4.5.0 (Quattro RS).

## Target System

- Laptop: Lenovo IdeaPad Slim 3 15IRH10
- CPU: 13th Gen Intel(R) Core(TM) i7-13620H
- GPU: Integrated graphics

## Configuration workflow

This setup is being rebuilt for Omarchy 4.5.0, one configuration at a time.
Implement the next step in `setup.py`, review it, and validate it before adding
another step. The script currently covers the steps through **Displays and Ten Workspaces per Monitor**,
in README order. Manual application setup is described
below. It uses Python 3 and TOMLKit, listed in `requirements.txt`.
Code follows the general and Python rules in the sibling `swe-standards`
repository.

The previous assets, installer, and tests were removed. Later sections are
retained as reference; their commands and file paths need to be reviewed for
4.5.0 before implementation. Git history retains
the previous source code. Do not restore it without reviewing compatibility.

On a fresh or reinstalled system, check each applicable section against the
current machine. Completion on a previous installation is historical context.
Skip steps whose checks already pass and apply missing prerequisites. Application
sign-ins and personal account synchronization remain manual steps.

## Clone This Repository

```bash
cd ~/Projects
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop.git
cd omarchy-configs-laptop
```

Create and activate the project virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Activate `.venv` in each terminal before running the script. Reinstall from
`requirements.txt` when dependencies change. TOMLKit preserves comments and
unrelated settings when updating TOML configuration.

## Ghost Pastel Theme

After reviewing the code, run it as your desktop user from an unlocked
graphical session, without `sudo` or command-line arguments:

```bash
python setup.py
```

The script uses `omarchy theme install` with the
[Ghost Pastel repository](https://github.com/row-huh/omarchy-ghost-pastel-theme)
if the theme is missing. Installation also activates the theme. If Ghost Pastel
is already installed, the script prints a message and skips it, even if another
theme is active.

The theme is installed under `~/.config/omarchy/themes/ghost-pastel`. A first
installation requires network access. The script checks the installed theme
list after installation. Verify that the list includes `Ghost Pastel`:

```bash
omarchy theme list
```

After a new installation, confirm the bar, wallpaper, and terminal colors
visually too. Custom border colors will be reviewed in the later window-layout
step.

## Brave

Run `python setup.py` to install Brave after the Ghost Pastel step. If the
`brave` executable is already available, the script prints a message and skips
installation. Otherwise, it uses Omarchy's browser installer:

```bash
omarchy install browser brave
```

The script checks that `brave` is available after installation. Then manually
set Brave as the default browser:

```bash
omarchy default browser brave
```

### Setup

1. Open Brave and set it as the default browser.
2. Go to **Settings → Appearance → Theme** and select **Dark**.
3. Go to **Settings → Sync** and select **I have a Sync Code**.
4. On your smartphone:
   1. Open Brave.
   2. Go to **Settings → Sync**.
   3. Select **Add a new device**.
   4. Scan the QR code displayed on your laptop.
5. Wait for synchronization to complete, including bookmarks, passwords, history, tabs, and other data.
6. Go to **Settings → Search engine** and set:
   - Normal: Google
   - Private: Google
7. ~~Go to **Settings → System** and disable **Use graphics acceleration when available**.~~

## WhatsApp

WhatsApp comes preinstalled as an Omarchy web app in this version.
`python setup.py` reads the current Omarchy version with `omarchy version` and
prints `WhatsApp already installed in version CURRENT_VERSION`. This step only
prints the message. Open WhatsApp from the app launcher and link your phone
manually.

## Slack

`python setup.py` only prints `Slack can be installed as a service.`
Slack installation and sign-in are manual steps. The web-app option is:

```bash
omarchy webapp install "Slack" "https://app.slack.com/client" ""
```

The empty icon argument lets Omarchy download Slack's icon automatically. Open
the app launcher with `Super + Space`, search for **Slack**, and sign in to the
workspace. Allow notifications when the browser prompts for permission.

If Brave is the configured default browser, Slack opens in a standalone Brave
web-app window.

## Discord

Discord comes preinstalled as an Omarchy web app in this version.
`python setup.py` reads the current Omarchy version with `omarchy version` and
prints `Discord already installed in version CURRENT_VERSION`. This step only
prints the message. Open the app launcher with `Super + Space`, search for
**Discord**, and sign in manually.

If Brave is the configured default browser, Discord opens in a standalone Brave
web-app window.

## Zathura

`python setup.py` installs any missing packages below and verifies that Zathura
loads its `pdf-mupdf` plugin. It then checks the PDF association, skips it if
already correct, or backs up the existing `mimeapps.list` before setting and
verifying Zathura as the default. Backups have a timestamp suffix alongside
the original file. The script respects `XDG_CONFIG_HOME`.

The equivalent manual steps are:

Install the reader, its PDF backend, and the XDG association tools. `omarchy pkg
add` skips packages that are already installed.

```bash
omarchy pkg add zathura zathura-pdf-mupdf xdg-utils
```

Run the association commands as the logged-in desktop user. If the association
already matches the check below, keep it. Otherwise, back up the existing MIME
configuration and set the PDF handler:

```bash
mimeapps="${XDG_CONFIG_HOME:-$HOME/.config}/mimeapps.list"
if [[ -f "$mimeapps" ]]; then
  cp -a -- "$mimeapps" "$mimeapps.backup-$(date +%Y%m%d-%H%M%S)"
fi
xdg-mime default org.pwmt.zathura.desktop application/pdf
```

Verify both PDF support and the default application:

```bash
zathura --version
xdg-mime query default application/pdf
```

The version output must list the `pdf-mupdf` plugin, and the MIME query must
return `org.pwmt.zathura.desktop`. Zathura's [document formats are provided by
plugins](https://pwmt.org/projects/zathura/plugins/), so installing the reader
alone is insufficient. The next section includes an optional manual PDF test
for checking the complete build-and-view workflow.

## LaTeX and Carlito

`python setup.py` installs missing packages and quietly verifies the tools and
TeX file lookups below. Existing packages are skipped. Routine runs print short
status messages without compiling a sample document or opening a PDF viewer.

The equivalent manual checks are:

Install the baseline for the MOVER Beamer slides and Portuguese activity reports:

```bash
omarchy pkg add texlive-binextra texlive-latexrecommended texlive-latexextra \
  texlive-fontsrecommended texlive-fontsextra texlive-pictures \
  texlive-langportuguese poppler
```

These packages provide `latexmk`, pdfLaTeX, Beamer/TikZ, the required font
collections, Portuguese language support, and PDF inspection tools. Project
Python environments and additional project-specific dependencies are described
in their own repositories.

The [TeX Live additional fonts collection](https://archlinux.org/packages/extra/any/texlive-fontsextra/)
provides [Carlito's TeX support](https://ctan.org/pkg/carlito), including the style,
font metrics, and map needed by `\usepackage[sfdefault]{carlito}`. TeX Live
registers the font map during installation; loading it explicitly again causes
duplicate fontmap warnings. The [desktop `ttf-carlito` package](https://archlinux.org/packages/extra/any/ttf-carlito/files/)
contains TTF fonts and Fontconfig settings; it does not supply these TeX files.
`texlive-fontsextra` is a large collection; `pacman -Si texlive-fontsextra` shows
its current download and installed sizes.

Check the tools and TeX's file lookup after installation:

```bash
command -v latexmk pdflatex pdffonts
kpsewhich beamer.cls
kpsewhich carlito.sty
kpsewhich carlito.map
kpsewhich mweights.sty
```

Every lookup must print a path. If Carlito files are missing, inspect
`pacman -Q texlive-fontsextra` and `pacman -Qkk texlive-fontsextra` before
continuing. Installing a desktop font or opening an existing PDF does not verify
that new PDFs can be built.

### Compile and open a test PDF (manual)

Run this only when you want to verify PDF compilation and viewing, such as on
a fresh installation or when troubleshooting. It exercises the same
pdfLaTeX/Carlito setup as the slides and keeps its output in a temporary folder:

```bash
smoke_dir=$(mktemp -d "${TMPDIR:-/tmp}/omarchy-carlito.XXXXXX")
cat > "$smoke_dir/carlito-check.tex" <<'TEX'
\documentclass{beamer}
\usepackage[sfdefault]{carlito}
\usefonttheme{professionalfonts}
\begin{document}
\begin{frame}{Carlito PDF check}
Regular text, \textbf{bold text}, \textit{italic text},
and \textbf{\textit{bold italic text}}.
\end{frame}
\end{document}
TEX
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory="$smoke_dir" "$smoke_dir/carlito-check.tex"
```

After compilation succeeds, inspect the embedded fonts and open the result from
the same terminal in an unlocked graphical session:

```bash
pdffonts "$smoke_dir/carlito-check.pdf"
xdg-open "$smoke_dir/carlito-check.pdf"
```

The font table should list `Crlt`, `Crlt-Bold`, `Crlt-Italic`, and
`Crlt-BoldItalic` with `emb` set to `yes`. These are Carlito's PDF font names.
Zathura should open the PDF. Then run each project's documented build to check its full
dependency set. Record any build failure before considering the setup complete.

## Touchpad Right Click

`python setup.py` reloads Hyprland, checks for configuration errors, and reads
the effective touchpad setting. If lower-right clicking is already enabled,
the step prints a message and skips editing. Otherwise, it appends the override
below to the existing `input.lua`, preserving unrelated settings and backing
up the original with a timestamp suffix. The script validates Lua syntax before
writing, reloads Hyprland, and verifies the setting. Failed validation restores
the backup and reloads the previous configuration. Run this from the active
graphical session, then test a lower-right touchpad click manually.

Use the touchpad's lower-right click area for right-click. In Hyprland, this is
controlled by the `clickfinger_behavior` touchpad setting:

Path: `~/.config/hypr/input.lua`

```lua
hl.config({
  input = {
    touchpad = {
      clickfinger_behavior = false,
    },
  },
})
```

## Neovim

### Neo-tree

`python setup.py` creates the visibility override below and skips it on later
runs if unchanged. Existing plugin specifications are retained as a nested
Lazy.nvim specification, followed by this visibility override so unrelated
options and plugins are preserved. Changed files are backed up beside the
original with a timestamp suffix. Lua syntax is checked before writing.

Show hidden, filtered, and Git-ignored items in Neo-tree by default while keeping their filtered styling.

Path: `~/.config/nvim/lua/plugins/neo-tree.lua`

```lua
return {
  {
    "nvim-neo-tree/neo-tree.nvim",
    opts = {
      filesystem = {
        filtered_items = {
          visible = true,
        },
      },
    },
  },
}
```

Restart Neovim to load the plugin override, then open Neo-tree and confirm
hidden and Git-ignored files are visible with their filtered styling.

### Image Rendering

`python setup.py` installs ImageMagick if its `magick` command is missing,
then creates or merges the image-rendering override. Existing plugin settings
are preserved, changed files are backed up, and Lua syntax is validated before
writing. An unchanged override is skipped.

Enable Snacks image rendering so supported image files can be displayed inside Neovim.

Path: `~/.config/nvim/lua/plugins/image-rendering.lua`

```lua
return {
  {
    "folke/snacks.nvim",
    opts = {
      image = {
        enabled = true,
      },
    },
  },
}
```

Restart Neovim after creating the file. Open an image in a terminal supporting
the Kitty graphics protocol, such as Ghostty or Kitty, and confirm it renders.
Run `:checkhealth snacks` if rendering fails. Configuration and syntax checks
alone do not verify terminal image support.

## Codex CLI Approval Defaults

`python setup.py` merges the defaults below using TOMLKit. It skips the edit
when all three top-level settings already match. Otherwise, it backs up the
existing file and validates the result with `codex features list`, restoring
the backup if validation fails. `CODEX_HOME` is respected when set. The Codex
CLI must already be installed; account sign-in remains manual.

Make **Approve for me** the default for new Codex CLI sessions.

Path: `~/.codex/config.toml`

Back up the existing file, then merge these settings at the top level, before
any TOML table headers. Preserve all unrelated settings.

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
sandbox_mode = "workspace-write"
```

Eligible approval requests go through automatic review. The workspace sandbox
remains enabled. These defaults apply to new sessions; existing sessions retain
their settings. Start a new session and use `/permissions` to check the active
permission mode.

Official references: [Auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review) and
[Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Steam

`python setup.py` prints a message and skips installation if the `steam`
executable is already available. Otherwise, it uses Omarchy's installer,
which selects the system's graphics dependencies, then checks that the
executable is available:

```bash
omarchy install gaming steam
```

Steam sign-in and game installation remain manual. Set these Dota 2 launch
options manually in Steam:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 %command% -console -novid
```

## Clock Format

`python setup.py` merges the three format settings below into the existing
clock entry, preserving its position, other widget options, and unrelated shell
settings. The built-in 4.5 clock supports week numbers, so a custom plugin is
unnecessary. If all formats match, the script prints a message and skips editing.

Changed files are backed up before the JSON is written atomically. If the user
configuration inherits the default bar layout, the script uses Omarchy's
installed layout as the starting point. A missing clock is added in the center;
duplicate clock entries are reported for resolution. An existing legacy
`lvasquez.clock` entry keeps its plugin ID.

Path: `~/.config/omarchy/shell.json`

```json
{
  "id": "omarchy.clock",
  "format": "dd MMM ddd · 'W'ww · HH:mm",
  "formatAlt": "dd MMM ddd · 'W'ww · HH:mm",
  "verticalFormat": "HH\n—\nmm"
}
```

The shell reloads the settings automatically. Confirm the displayed date, week
number, and time in the bar after running the script.

## Battery Format

`python setup.py` enables the percentage beside the battery icon using the
built-in `omarchy.power` widget. It skips an existing `showPercentage: true`,
preserves the widget's position and unrelated settings, and backs up changes
before writing JSON atomically. A missing power widget is added on the right;
duplicate entries are reported for resolution. An existing legacy
`lvasquez.power` entry keeps its plugin ID.

Path: `~/.config/omarchy/shell.json`

```json
{
  "id": "omarchy.power",
  "showPercentage": true
}
```

The shell reloads the settings automatically. Confirm the percentage appears
beside the battery icon in the horizontal bar.

### Battery Panel Refresh

`python setup.py` changes the open power panel's refresh interval from five
seconds to two seconds. It clones the installed `omarchy.power` plugin with
`omarchy plugin clone omarchy.power`, producing `~/.config/omarchy/plugins/<username>.power/`.
An existing clone is reused. The step changes only the refresh timer in
`Panel.qml`, preserving the rest of the current plugin.

QML syntax is validated before editing. Backups of affected files are stored
under `${XDG_STATE_HOME:-$HOME/.local/state}/omarchy/backups/power-widget-<timestamp>/`,
outside the watched plugin directory. The shell is restarted to load the
change. If activation fails, the script restores the previous files and removes
a clone created by this attempt. An active two-second configuration is skipped.
An unexpected timer implementation stops the step for review.

Open the battery panel and confirm details refresh every two seconds; close it
and confirm polling stops. The percentage continues to update through UPower
independently.

### Charging Icon

The charging icon follows UPower's AC/battery state without waiting for its
charging-rate or time-to-full estimates. Those estimates can lag plug-in by
about 10 seconds or fluctuate during charging. The custom `Model.js` uses
UPower's `PendingCharge` state, or `FullyCharged` below 99%, to recognize a
charge hold; it does not infer a hold from a zero rate or a long estimate.

`python setup.py` applies this change to the power clone created by the
preceding refresh step. It runs the Node.js regression checks against a staged
model before editing, backs up `Model.js` under
`${XDG_STATE_HOME:-$HOME/.local/state}/omarchy/backups/charging-icon-<timestamp>/`,
and restarts the shell. A failed restart restores the backup. An unchanged
model is skipped; unfamiliar charge-hold logic stops the step for review.

Node.js is required for the regression checks. To run them manually against
the current user's clone:

```bash
POWER_MODEL_PATH="$HOME/.config/omarchy/plugins/$USER.power/Model.js" \
  node tests/power-model.test.cjs
```

Unplug the charger, wait five seconds, and plug it back in. Confirm that the
charging icon appears promptly and stays visible while charging, including
with the battery panel closed. Model tests do not replace this live check.

## Agents Widget

Use the default `omarchy.agents` widget supplied by Omarchy 4.5.0.
`python setup.py` only prints `Using default Agents widget from Omarchy version
CURRENT_VERSION`, reading the installed version with `omarchy version`.
Provider preferences and account setup remain in Omarchy's current interface.

## Compact Window Layout and Focus Border

`python setup.py` appends the reviewed
[compact layout configuration](config/hypr/compact-layout.lua) to
`~/.config/hypr/looknfeel.lua`, preserving existing appearance settings. It sets
inner and outer window gaps to zero and border width to three pixels.

The Lua block reads the current theme's `colors.toml` on every Hyprland reload.
Focused borders use `color6`, falling back to `accent`; inactive borders use
`background`. The same colors apply to grouped windows. Six- and eight-digit
hex colors are supported. If the needed palette fields are unavailable, the
existing theme's border colors are retained.

The script validates Lua syntax, backs up changed files with a timestamp
suffix, reloads Hyprland, and checks `hyprctl configerrors`. A failed reload
restores the original file and reloads it. An unchanged configuration is
skipped after validating the existing Hyprland configuration.

After running the script, focus different windows and confirm the spacing,
three-pixel borders, and theme colors. Repeat the visual check after switching
themes.

## Displays and Ten Workspaces per Monitor

`python setup.py` appends the reviewed [display profiles](config/hypr/displays.lua)
to `~/.config/hypr/monitors.lua`. Existing fallback rules, GTK scaling, and
unrelated monitor settings are preserved. Changed files are backed up, Lua
syntax is validated, and Hyprland is reloaded and checked for configuration
errors. A failed reload restores the backup. An unchanged override is skipped.

The display profiles are:

- Laptop `eDP-1`: preferred resolution, positioned to the left, retaining the
  existing `omarchy_monitor_scale` value. If that variable is absent, Hyprland's
  automatic scale is used.
- Samsung LU28R55 (`HX5W200353`): 1920×1080 at 60 Hz, scale 1, at `0x0`.
- BenQ G610HDAL (`A5B03247019`): 1366×768 at 59.79 Hz, scale 1, using
  `auto-right` so it can sit beside the Samsung rather than overlap it.

External monitors are matched by their descriptions, including model and serial,
so their connector names can change across docks. Unrecognized monitors keep
the existing fallback rule. Placement follows Hyprland's
[automatic positioning](https://wiki.hypr.land/configuring/core/monitors/positioning/).
The monitor calls stay on single lines so Omarchy's clamshell helper can read
the laptop's position and scale.

Workspaces use **Omarchy 4.5's native ten slots per monitor**. The script prints
`Using native Omarchy workspace behavior: 10 workspaces per monitor in version CURRENT_VERSION`.
The bar labels each monitor's workspaces locally, while Hyprland's underlying
IDs use blocks of ten. `Super + 1` through `Super + 0` select slots on the
focused monitor; the default window-moving shortcuts are retained. Native
docking and clamshell handling manage workspace migration when screens are
connected, disconnected, or disabled. No custom workspace-placement module is
installed.

The stock workspace widget always shows the first five slots and adds later
slots only when they exist. `python setup.py` clones `omarchy.workspaces` into
`~/.config/omarchy/plugins/<username>.workspaces/` and changes its button list
to show all ten slots, including empty ones. The tenth button is labeled `0`,
matching the keyboard shortcut; the active button keeps Omarchy's layout glyph.
Guest workspaces remain visible after the monitor's own ten slots.

The step validates QML and runs workspace-list checks before changing the
widget. Backups are stored under
`${XDG_STATE_HOME:-$HOME/.local/state}/omarchy/backups/workspaces-widget-<timestamp>/`.
It restarts the shell after activation, restores previous files if that fails,
and skips an already active, updated clone. It changes the bar display while
retaining Omarchy's native workspace manager.

After applying, check the live output:

```bash
hyprctl monitors all
hyprctl configerrors
hyprctl -j workspaces | jq 'sort_by(.id) | map({id, monitor, windows})'
```

Verify each external monitor's resolution and refresh rate when connected.
If both are connected, confirm they do not overlap and the laptop stays left.
Test workspace shortcuts on each focused monitor, then unplug/reconnect the
external display and close/reopen the lid while docked. These hardware checks
remain necessary; only the laptop display was connected during development.

## Clock Refresh Safeguard

The previous setup included a custom clock plugin and a user systemd timer
that requested a refresh every 30 seconds to address stale displays after
resume. The files were removed during the reset. Their presence in Git history
does not establish that the workaround was tested or is needed on 4.5.0.

Revisit this only if a stale clock can be reproduced, then test the fix across
suspend and resume before including it in setup.

## Experimental: Intel GPU Driver Update

Update Omarchy, the kernel, and Intel graphics packages together:

```bash
omarchy update
omarchy system reboot
lspci -k -s 00:02.0
```

## Apply Configs with an Agent

Implement one reviewed section at a time in `setup.py` rather than copying an
entire configuration tree. Apply it to the live desktop when the user requests.
Before changing each destination, back up its existing contents and inspect
its current settings. Merge the documented overrides while retaining unrelated
user settings and Omarchy's default imports. Skip settings already applied.

### Custom plugin installation

The old plugin sources and installer were removed. Review each widget against
the stock 4.5.0 implementation before reintroducing custom code. Install any
reviewed user-owned plugins under `~/.config/omarchy/plugins/`, back up changed
destinations, and preserve executable permissions on collectors. Packaged
plugins under `/usr/share/omarchy/` stay untouched.

The current setup uses the built-in `omarchy.clock` and `omarchy.agents`
widgets. The reviewed power and workspace-display customizations use the
`<username>.power` and `<username>.workspaces` clones created by Omarchy's CLI.
Preserve widget positions and unrelated bar options when applying these steps.

### Verification and recovery

Validate edited Lua files with `luac -p` and JSON files with
`python -m json.tool` before applying. Reload Hyprland and check
`hyprctl configerrors`; verify the native ten-workspace slots on each monitor.
Restart Omarchy Shell after installing reviewed plugins and verify the affected
widgets in the running shell. Restart Neovim to load its plugin overrides.

For a fresh installation, also complete the **Zathura** and **LaTeX and Carlito**
dependency checks. The compilation and PDF-viewing example is a separate manual
check. Routine setup must not compile or open sample PDFs. Verify prerequisites
from the installed system instead of relying on a previous machine's completion
history.

If a change fails validation, restore the affected files from the backups and
reload the affected component. Report what was applied and any remaining work.
The experimental GPU update and reboot are a separate optional operation;
perform them only when the user asks for that update.
