# Omarchy Laptop Config

Personal configuration for Omarchy Quattro.

## Target System

- Laptop: Lenovo IdeaPad Slim 3 15IRH10
- CPU: 13th Gen Intel(R) Core(TM) i7-13620H
- GPU: Integrated graphics

## Configuration workflow

`README.md` is the setup specification for Omarchy Quattro. Agents apply its
instructions directly to the laptop's user configuration, preserving unrelated
settings. The former comparison/deployment scripts, manifest, and duplicate
`.config` snapshot have been retired; Git history retains them.

Custom plugins and workspace logic live in `assets/` because their complete
implementations are needed to reproduce the setup. Installation steps below
identify their destinations. These are source assets, not a home-directory
snapshot.

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
7. ~~Go to **Settings → System** and disable **Use graphics acceleration when available**.~~

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
`assets/plugins/lvasquez.power/Panel.qml`). The bar percentage continues
to update through UPower independently. The timer runs only while the panel is
open, and saved plugin changes reload automatically in Omarchy Shell.

## Agents Widget

The managed `lvasquez.agents` plugin preserves the live agents widget and its
local usage collectors, including the Codex RPC read timeout fix. Its source,
assets, and executable collectors are preserved in `assets/plugins/lvasquez.agents/`.
Install this directory using the plugin instructions below.

## Compact Window Layout and Focus Border

Path: `~/.config/hypr/looknfeel.lua`

```lua
-- Change the default Omarchy look'n'feel.

local function load_current_theme_colors()
  local colors = {}
  local home = os.getenv("HOME")

  if not home then
    return colors
  end

  local file = io.open(home .. "/.local/state/omarchy/current/theme/colors.toml", "r")

  if not file then
    return colors
  end

  for line in file:lines() do
    local name, value = line:match('^%s*([%w_]+)%s*=%s*"([^"]+)"')

    if name then
      colors[name] = value
    end
  end

  file:close()
  return colors
end

local function to_hypr_color(value)
  if not value then
    return nil
  end

  local hex = value:match("^#(%x+)$")

  if hex and #hex == 6 then
    return "rgb(" .. hex .. ")"
  elseif hex and #hex == 8 then
    return "rgba(" .. hex .. ")"
  end

  return value
end

local theme_colors = load_current_theme_colors()
local active_border_color = to_hypr_color(theme_colors.color6 or theme_colors.accent)
local inactive_border_color = to_hypr_color(theme_colors.background)
local general = {
  gaps_in = 0,
  gaps_out = 0,
  border_size = 3,
}
local config = { general = general }

if active_border_color and inactive_border_color then
  general.col = {
    active_border = active_border_color,
    inactive_border = inactive_border_color,
  }

  config.group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  }
end

-- https://wiki.hypr.land/Configuring/Basics/Variables/#general
hl.config(config)
```

The code reads the current theme palette on each reload.

## Displays and Ten Workspaces

The laptop screen sits to the left of external monitors. Monitor rules match
model and serial, so the Samsung's resolution is not applied to the BenQ.

- BenQ G610HDAL (`A5B03247019`): 1366×768 at 59.79 Hz, scale 1.
  With the lid open, workspaces 1–7 belong to the laptop and 8–10 to the BenQ.
- Samsung LU28R55 (`HX5W200353`): 1920×1080 at 60 Hz, scale 1.
  Other external monitors retain the earlier workspace-7 split.
- With the internal screen disabled, all ten workspaces use the external screen.
- With no external screen, all ten workspaces use the laptop.

Set the monitor rules in `~/.config/hypr/monitors.lua`:

```lua
-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
-- List current monitors and supported resolutions with: hyprctl monitors all

local omarchy_gdk_scale = 2
local omarchy_monitor_scale = "auto"

hl.env("GDK_SCALE", tostring(omarchy_gdk_scale))
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = omarchy_monitor_scale })

-- Samsung external display: 1080p at 60 Hz.
hl.monitor({ output = "desc:Samsung Electric Company LU28R55 HX5W200353", mode = "1920x1080@60", position = "0x0", scale = 1 })

-- BenQ G610HDAL: preferred panel resolution, without scaling.
hl.monitor({ output = "desc:BNQ BenQ G610HDAL A5B03247019", mode = "1366x768@59.79", position = "0x0", scale = 1 })

-- Place the laptop to the left of external displays.
hl.monitor({ output = "eDP-1", mode = "preferred", position = "auto-left", scale = omarchy_monitor_scale })
```

Copy `assets/hypr/workspace-monitors.lua` to
`~/.config/hypr/workspace-monitors.lua`. Add this once to
`~/.config/hypr/hyprland.lua`, after the default and personal config imports:

```lua
require("hypr.workspace-monitors")
```

The module handles monitor events and moves existing workspaces automatically.

After applying these settings, verify with:

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

Create `~/.config/systemd/user/omarchy-clock-refresh.service` with:

```ini
[Unit]
Description=Refresh the Omarchy clock independently of QML timers
PartOf=graphical-session.target

[Service]
Type=oneshot
ExecStart=/usr/bin/timeout 8 /usr/bin/omarchy-shell omarchy.clock refresh
TimeoutStartSec=10
```

Create `~/.config/systemd/user/omarchy-clock-refresh.timer` with:

```ini
[Unit]
Description=Keep the Omarchy clock current across suspend and resume
PartOf=graphical-session.target

[Timer]
OnCalendar=*-*-* *:*:00,30
OnActiveSec=2
AccuracySec=1s
Persistent=true
Unit=omarchy-clock-refresh.service

[Install]
WantedBy=graphical-session.target
```

After applying the repository on a fresh installation, run these commands from
an unlocked graphical session to load the plugins and enable the timer:

```bash
systemctl --user daemon-reload
omarchy restart shell
systemctl --user enable --now omarchy-clock-refresh.timer
omarchy-shell omarchy.clock status
systemctl --user list-timers omarchy-clock-refresh.timer
```

No Stay Awake sleep-blocking service is included.

## Experimental: Intel GPU Driver Update

Update Omarchy, the kernel, and Intel graphics packages together:

```bash
omarchy update
omarchy system reboot
lspci -k -s 00:02.0
```

## Apply Configs with an Agent

Follow the sections above rather than copying an entire configuration tree.
Before changing each destination, back up its existing contents and inspect
its current settings. Merge the documented overrides while retaining unrelated
user settings and Omarchy's default imports. Skip settings already applied.

### Custom plugin installation

Copy each directory in `assets/plugins/` to the matching directory under
`~/.config/omarchy/plugins/`, preserving executable permissions on `usage-codex`
and `usage-update`. Back up any existing destination first. These user-owned
plugins preserve the custom clock refresh, power panel polling, and agent usage
collector behavior; do not modify packaged plugins under `/usr/share/omarchy/`.

In `~/.config/omarchy/shell.json`, merge the clock and battery settings shown
above into the existing bar entries, replacing `omarchy.clock` with
`lvasquez.clock` and `omarchy.power` with `lvasquez.power`. Replace
`omarchy.agents` with `lvasquez.agents` in the existing agents entry. If no agents
entry exists, insert `{ "id": "lvasquez.agents" }` in `bar.layout.right` after
the tray entry. Preserve other bar entries and shell settings.

### Verification and recovery

Validate edited Lua files with `luac -p` and JSON files with
`python -m json.tool` before applying. Reload Hyprland and check
`hyprctl configerrors`; confirm workspaces 1–10 and their monitor assignments.
Restart Omarchy Shell after installing the plugins, then enable and verify the
clock timer using the commands in **Clock Refresh Safeguard**. Verify the clock,
battery panel, and agents widget in the running shell. Restart Neovim to load
its plugin overrides.

If a change fails validation, restore the affected files from the backups and
reload the affected component. Report what was applied and any remaining work.
The experimental GPU update and reboot are a separate optional operation;
perform them only when the user asks for that update.
