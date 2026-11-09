-- config/hypr/discord-workspace.lua

hl.on("window.open", function(window)
  local class = (window.class or window.initial_class or ""):lower()
  if class ~= "discord" and not class:match("^[%w%-]+%-discord%.com__") then
    return
  end

  local monitor = window.monitor or hl.get_active_monitor()
  if not monitor then
    return
  end

  local target = o.workspaces.workspace_id(monitor, 8)
  if window.workspace and window.workspace.id == target then
    return
  end

  if #hl.get_workspace_windows(tostring(target)) > 0 then
    return
  end

  hl.dispatch(hl.dsp.window.move({
    workspace = tostring(target),
    window = "address:" .. window.address,
    follow = false,
  }))
end)
