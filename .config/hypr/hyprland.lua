-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Omarchy's bootstrap keeps path setup out of this user config.
dofile((os.getenv("OMARCHY_PATH") or "/usr/share/omarchy") .. "/default/hypr/bootstrap.lua")

-- Load Omarchy defaults.
require("default.hypr.omarchy")

-- Load personal overrides after the defaults.
require("hypr.monitors")
require("hypr.input")
require("hypr.bindings")
require("hypr.looknfeel")
require("hypr.autostart")

-- Toggle config flags dynamically.
require("default.hypr.toggles")

-- Keep ten persistent workspaces. With an external display connected,
-- workspace 7 belongs to the external display while the lid is open.
-- In clamshell mode all ten workspaces belong to the external display.
local external_monitor
local state_home = os.getenv("XDG_STATE_HOME") or (os.getenv("HOME") .. "/.local/state")
local clamshell_flag = io.open(state_home .. "/omarchy/toggles/hypr/internal-monitor-clamshell.lua", "r")
local clamshell = clamshell_flag ~= nil
if clamshell_flag then clamshell_flag:close() end

for _, monitor in ipairs(hl.get_monitors()) do
  if monitor.name ~= "eDP-1" and not monitor.disabled then
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
    if clamshell then
      rule.monitor = external_monitor
      rule.default = workspace == 1
    elseif workspace == 7 then
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
