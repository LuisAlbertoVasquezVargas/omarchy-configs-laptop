# Omarchy Laptop Config

Personal configuration for Omarchy Quattro.

## Target System

- Laptop: Lenovo IdeaPad Slim 3 15IRH10
- CPU: 13th Gen Intel(R) Core(TM) i7-13620H
- GPU: Integrated graphics

<!-- TODO: Describe additional hardware components. -->

## Clone This Repository

```bash
cd ~/Projects
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop.git
cd omarchy-configs-laptop
```

## Brave

```bash
omarchy install browser brave
omarchy default browser brave
```

## WhatsApp

> **TODO:** Choose between Ferdium and Quattro's built-in WhatsApp web app.

## Slack

> **TODO:** Choose between Ferdium and a Quattro web app. Disable GPU acceleration persistently before using Slack through Ferdium.

## Zathura

```bash
omarchy pkg add zathura zathura-pdf-mupdf
xdg-mime default org.pwmt.zathura.desktop application/pdf
```

## Neovim

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

## Compact Window Layout

Path: `~/.config/hypr/looknfeel.lua`

```lua
hl.config({
  general = {
    gaps_in = 0,
    gaps_out = 0,
    border_size = 0,
  },
})
```

## Seven Workspaces

Configure Hyprland to use only workspaces 1-7, including when an external monitor is connected.

Without an explicit monitor assignment, Hyprland may place all persistent workspaces on the laptop display and create workspace 8 for the external display. This configuration assigns workspace 7 to the external monitor when one is detected.

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

for workspace = 1, 7 do
  local rule = {
    workspace = tostring(workspace),
    persistent = true,
  }

  -- Every enabled monitor needs an active workspace. Keep the external
  -- display on workspace 7 so Hyprland does not create workspace 8 for it.
  if workspace == 7 and external_monitor then
    rule.monitor = external_monitor
    rule.default = true
  end

  hl.workspace_rule(rule)
end
```

When the external monitor is disconnected, Hyprland moves its workspaces and windows to the remaining display. Running `hyprctl reload` while undocked reevaluates the monitor detection and leaves workspaces 1-7 on the built-in display.

If the laptop session starts undocked and an external monitor is connected later, run `hyprctl reload` so workspace 7 is assigned to it.

### Disable workspace 8-10 shortcuts

Omarchy provides numeric bindings for workspaces 1-10 by default. Disable switching to or moving windows to workspaces 8-10.

Path: `~/.config/hypr/bindings.lua`

```lua
-- Limit numeric workspace bindings to the seven persistent workspaces.
for workspace = 8, 10 do
  local key = "code:" .. tostring(workspace + 9)

  hl.unbind("SUPER + " .. key)
  hl.unbind("SUPER + SHIFT + " .. key)
  hl.unbind("SUPER + SHIFT + ALT + " .. key)
end
```

### Reload and validate Hyprland

```bash
hyprctl reload
hyprctl configerrors
```

`hyprctl configerrors` should return no output.

### Remove an existing workspace 8

If workspace 8 was already created, check whether it contains any windows:

```bash
hyprctl -j clients | jq \
  '[.[] | select(.workspace.id > 7 and .workspace.id <= 10) |
  {address, class, title, workspace: .workspace.id}]'
```

Move each listed window to workspace 7, replacing the example address with the address reported by the previous command:

```bash
hyprctl dispatch \
  'hl.dsp.window.move({ workspace = "7", follow = false, window = "address:0xWINDOW_ADDRESS" })'
```

Window addresses change between sessions and must not be hardcoded.

Activate workspace 7 on the external display and reload:

```bash
hyprctl dispatch 'hl.dsp.focus({ workspace = "7" })'
hyprctl reload
```

### Verify the result

```bash
hyprctl -j workspaces | jq \
  'sort_by(.id) | map({id, monitor, windows})'
```

The workspace IDs should be exactly 1-7.

Confirm that no bindings for workspaces 8-10 remain:

```bash
hyprctl -j binds | jq \
  '[.[] |
  select((.description // "") |
  test("workspace (8|9|10)$"; "i")) |
  .description]'
```

The expected result is:

```text
[]
```

## Experimental: Codex Workspace Shortcut

Path: `~/.config/hypr/bindings.lua`

```lua
local function codex_workspace(key, workspace, path)
  local rules = { workspace = workspace .. " silent" }

  o.bind(key, "Codex + terminal (workspace " .. workspace .. ")", hl.dsp.focus({ workspace = workspace }))
  o.bind(key, nil, hl.dsp.exec_cmd(o.launch('xdg-terminal-exec --dir="' .. path .. '" codex -C "' .. path .. '"'), rules))
  o.bind(key, nil, hl.dsp.exec_cmd(o.launch('xdg-terminal-exec --dir="' .. path .. '"'), rules))
end

codex_workspace("SUPER + Prior", "2", os.getenv("HOME") .. "/Projects/MOVER-research-materials") -- Page Up / Re Pág
codex_workspace("SUPER + Next", "3", os.getenv("HOME") .. "/Projects/shopping-list-ui") -- Page Down / Av Pág
```

## Experimental: Intel GPU Driver Update

Update Omarchy, the kernel, and Intel graphics packages together:

```bash
omarchy update
omarchy system reboot
lspci -k -s 00:02.0
```

## Apply Configs

> **TODO:** Adapt `scripts/apply_configs.py` for Omarchy Quattro.
