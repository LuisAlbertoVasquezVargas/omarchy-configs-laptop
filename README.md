# Omarchy Laptop Config

Personal configuration for Omarchy Quattro.

## Target System

- Laptop: Lenovo IdeaPad Slim 3 15IRH10
- CPU: 13th Gen Intel(R) Core(TM) i7-13620H
- GPU: Integrated graphics

## Managed Configuration

This repository intentionally manages only the Quattro overrides listed in
`config-manifest.toml`:

- Hyprland bootstrap, workspace rules, bindings, look and feel, monitors,
  input overrides, and autostart overrides
- Omarchy Shell clock and battery presentation, plus custom clock, power, and agents plugins and the clock refresh timer
- Neovim Neo-tree and image-rendering overrides

Legacy Hyprland `.conf`, Waybar, and unused terminal files are not managed or
deployed. Every file under the repository's `.config` directory must have an
explicit manifest entry, so adding an unlisted file causes the tools to stop.

## Clone This Repository

```bash
cd ~/Projects
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop.git
cd omarchy-configs-laptop
```

## Ghost Pastel Theme

Install and activate the Ghost Pastel community theme:

```bash
omarchy theme install https://github.com/row-huh/omarchy-ghost-pastel-theme
```

The theme is installed under `~/.config/omarchy/themes/ghost-pastel`.

No Ghost Pastel-specific border override is required. The window configuration
reads the currently applied theme's `colors.toml`: `color6` supplies the focused
border and `background` supplies the inactive border.

## Brave

Install Brave:

```bash
omarchy install browser brave
```

Then set Brave as the default browser:

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
7. Go to **Settings → System** and disable **Use graphics acceleration when available**.

## WhatsApp

Nothing to install. WhatsApp comes preinstalled as an Omarchy web app.

## Slack

Install Slack as an Omarchy web app:

```bash
omarchy webapp install "Slack" "https://app.slack.com/client" ""
```

The empty icon argument lets Omarchy download Slack's icon automatically. Open the app launcher with `Super + Space`, search for **Slack**, and sign in to the workspace. Allow notifications when Brave prompts for permission.

Because Brave is the configured default browser, Slack opens in a standalone Brave web-app window.

## Discord

Nothing to install. Discord comes preinstalled as an Omarchy web app. Open the app launcher with `Super + Space`, search for **Discord**, and sign in.

Because Brave is the configured default browser, Discord opens in a standalone Brave web-app window.

## Zathura

```bash
omarchy pkg add zathura zathura-pdf-mupdf
xdg-mime default org.pwmt.zathura.desktop application/pdf
```

## Touchpad Right Click

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

Restart Neovim or reopen Neo-tree to apply the change.

### Image Rendering

Enable Snacks image rendering so supported image files can be displayed inside Neovim.

Path: `~/.config/nvim/lua/plugins/image-rendering.lua`

```lua
return {
  {
    "folke/snacks.nvim",
    opts = {
      image = {},
    },
  },
}
```

Restart Neovim after creating the file.

## Steam

```bash
omarchy install gaming steam
```

Dota 2 launch options:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 %command% -console -novid
```

## Clock Format

Migrates the previous Waybar clock format to Omarchy Shell.

Path: `~/.config/omarchy/shell.json`

```json
{
  "id": "lvasquez.clock",
  "format": "dd MMM ddd · 'W'ww · HH:mm",
  "formatAlt": "dd MMM ddd · 'W'ww · HH:mm",
  "verticalFormat": "HH\n—\nmm"
}
```

## Battery Format

Migrates the previous Waybar `{capacity}% {icon}` battery format to Omarchy Shell so the percentage remains visible beside the battery icon.

Path: `~/.config/omarchy/shell.json`

```json
{
  "id": "lvasquez.power",
  "showPercentage": true
}
```

### Battery Panel Refresh

The managed `lvasquez.power` plugin is a user-owned clone of `omarchy.power`.
Its open panel refreshes battery details, power profiles, and system stats every
2 seconds (`interval: 2000` in
`.config/omarchy/plugins/lvasquez.power/Panel.qml`). The bar percentage continues
to update through UPower independently. The timer runs only while the panel is
open, and saved plugin changes reload automatically in Omarchy Shell.

## Agents Widget

The managed `lvasquez.agents` plugin preserves the live agents widget and its
local usage collectors, including the Codex RPC read timeout fix. Its source,
assets, and executable collectors are included in the configuration manifest.

## Compact Window Layout and Focus Border

Path: `~/.config/hypr/looknfeel.lua`

```lua
local theme_colors = load_current_theme_colors()
local active_border_color = to_hypr_color(theme_colors.color6 or theme_colors.accent)
local inactive_border_color = to_hypr_color(theme_colors.background)
```

The tracked file defines `load_current_theme_colors()` and `to_hypr_color()`.
They read Omarchy's current `colors.toml` and translate its hex values into
Hyprland colors on every reload. Switching themes therefore changes both border
colors without editing `looknfeel.lua` or any individual theme. If a theme does
not expose these palette fields, the code leaves Omarchy's generated border
colors unchanged rather than introducing a hardcoded fallback.

## Displays and Ten Workspaces

The laptop screen sits to the left of external monitors. Monitor rules match
model and serial, so the Samsung's resolution is not applied to the BenQ.

- BenQ G610HDAL (`A5B03247019`): 1366×768 at 59.79 Hz, scale 1.
  With the lid open, workspaces 1–7 belong to the laptop and 8–10 to the BenQ.
- Samsung LU28R55 (`HX5W200353`): 1920×1080 at 60 Hz, scale 1.
  Other external monitors retain the earlier workspace-7 split.
- With the internal screen disabled, all ten workspaces use the external screen.
- With no external screen, all ten workspaces use the laptop.

`hypr/workspace-monitors.lua` handles monitor events and moves existing
workspaces automatically. It is loaded by `hypr/hyprland.lua`.

After deployment, verify with:

```bash
hyprctl reload
hyprctl configerrors
hyprctl -j workspaces | jq 'sort_by(.id) | map({id, monitor, windows})'
```

## Clock Refresh Safeguard

The local `lvasquez.clock` plugin supports an explicit refresh and a diagnostic
status call. A user systemd timer requests a refresh every 30 seconds, independently
of the shell's QML timers, to correct stale clock displays after resume. This is
a workaround; it does not block suspend or restart the shell periodically.

After applying the repository on a fresh installation, run these commands from
an unlocked graphical session to load the plugins and enable the timer:

```bash
systemctl --user daemon-reload
omarchy restart shell
systemctl --user enable --now omarchy-clock-refresh.timer
omarchy-shell omarchy.clock status
systemctl --user list-timers omarchy-clock-refresh.timer
```

The deployment script copies the service and timer files but does not enable
systemd units automatically. No Stay Awake sleep-blocking service is included.

## Experimental: Intel GPU Driver Update

Update Omarchy, the kernel, and Intel graphics packages together:

```bash
omarchy update
omarchy system reboot
lspci -k -s 00:02.0
```

## Apply Configs

The deployment tools use `config-manifest.toml` as an allowlist. They never
recursively deploy arbitrary files from `.config`.

### Compare

Compare the repository with the current home directory without changing
anything:

```bash
python scripts/compare_configs.py
```

Use JSON output for automation:

```bash
python scripts/compare_configs.py --json
```

Exit status `0` means every managed file matches, `1` means configuration
drift was found, and `2` means an unsafe target or configuration error was
detected.

### Preview and Apply

`apply_configs.py` is a dry run unless `--apply` is passed:

```bash
python scripts/apply_configs.py
python scripts/apply_configs.py --apply
```

Before writing, the script validates every JSON and Lua source file. It refuses
symbolic links and non-regular targets, backs up replacements, writes files
atomically, and validates the deployed files again. In an active Hyprland
session it also reloads Hyprland, checks `configerrors`, and verifies workspace IDs
1-10. A failed validation
automatically restores the backup.

Backups are stored under:

```text
~/.local/state/omarchy-configs/backups/<transaction-id>/
```

### Roll Back

Restore a deployment by using the transaction ID printed after a successful
apply:

```bash
python scripts/apply_configs.py --rollback <transaction-id>
```

Rollback refuses to delete or overwrite a managed file if it has been edited
since deployment.

### Tests

Run the isolated deployment tests without touching the live home directory:

```bash
python -m unittest discover -s tests -v
```
