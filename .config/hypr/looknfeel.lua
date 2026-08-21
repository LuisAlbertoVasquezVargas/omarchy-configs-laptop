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

-- https://wiki.hypr.land/Configuring/Basics/Variables/#decoration
-- hl.config({
--   decoration = {
--     -- Use round window corners.
--     rounding = 8,
--
--     -- Dim unfocused windows (0.0 = no dim, 1.0 = fully dimmed).
--     dim_inactive = true,
--     dim_strength = 0.15,
--   },
-- })

-- https://wiki.hypr.land/Configuring/Basics/Variables/#animations
-- hl.config({
--   animations = {
--     -- Disable all animations.
--     enabled = false,
--   },
-- })

-- https://wiki.hypr.land/Configuring/Basics/Variables/#layout
-- hl.config({
--   layout = {
--     -- Avoid overly wide single-window layouts on wide screens.
--     single_window_aspect_ratio = { 1, 1 },
--   },
-- })

-- https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/
-- hl.config({
--   scrolling = {
--     -- See only one column per screen instead of two.
--     column_width = 0.97,
--   },
-- })
