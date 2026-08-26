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

-- Keep seven persistent workspaces. With an external display connected,
-- workspaces 1-6 stay on the laptop and workspace 7 belongs to the external
-- display. Explicit assignments prevent Hyprland from creating workspace 8.
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
