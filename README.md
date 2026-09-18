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
- Omarchy Shell clock and battery presentation
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

Enable clickfinger behavior so clicking with two fingers produces a right click
on the touchpad. In Hyprland, this is the `clickfinger_behavior` touchpad
setting:

Path: `~/.config/hypr/input.lua`

```lua
hl.config({
  input = {
    touchpad = {
      clickfinger_behavior = true,
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
  "id": "omarchy.clock",
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
  "id": "omarchy.power",
  "showPercentage": true
}
```

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

## Ten Workspaces

Configure Hyprland to keep workspaces 1-10 persistent, including when an external monitor is connected.

With an external monitor connected, this configuration assigns workspace 7 to the external monitor and keeps the other workspaces on the laptop display. Omarchy's default shortcuts for workspaces 1-10 remain enabled.

### Create the persistent workspaces

Path: `~/.config/hypr/hyprland.lua`

```lua
local external_monitor

for _, monitor in ipairs(hl.get_monitors()) do
  if monitor.name ~= "eDP-1" then
    external_monitor = monitor.name
    break
  end
end

for workspace = 1, 10 do
  local rule = {
    workspace = tostring(workspace),
    persistent = true,
  }

  if external_monitor then
    if workspace == 7 then
      rule.monitor = external_monitor
      rule.default = true
    else
      rule.monitor = "eDP-1"

      if workspace == 1 then
        rule.default = true
      end
    end
  end

  hl.workspace_rule(rule)
end
```

When the external monitor is disconnected, Hyprland moves its workspaces and windows to the remaining display. Running `hyprctl reload` while undocked reevaluates the monitor detection and leaves workspaces 1-10 on the built-in display.

If the laptop session starts undocked and an external monitor is connected later, run `hyprctl reload` so workspace 7 is assigned to it.

### Reload and validate Hyprland

```bash
hyprctl reload
hyprctl configerrors
```

`hyprctl configerrors` should return no output.

### Verify the result

```bash
hyprctl -j workspaces | jq \
  'sort_by(.id) | map({id, monitor, windows})'
```

The workspace IDs should be exactly 1-10. The default numeric shortcuts for all ten workspaces should remain available.

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
