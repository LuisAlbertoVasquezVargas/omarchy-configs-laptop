-- Keep only personal keybinding overrides here. Omarchy defaults load first.

-- Limit numeric workspace bindings to the seven persistent workspaces.
for workspace = 8, 10 do
  local key = "code:" .. tostring(workspace + 9)

  hl.unbind("SUPER + " .. key)
  hl.unbind("SUPER + SHIFT + " .. key)
  hl.unbind("SUPER + SHIFT + ALT + " .. key)
end
