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
