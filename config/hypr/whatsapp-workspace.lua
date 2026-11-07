-- config/hypr/whatsapp-workspace.lua

hl.on("window.open", function(window)
  local class = window.initial_class or window.class or ""
  if not class:match("^[%w%-]+%-web%.whatsapp%.com__%-") then
    return
  end

  local monitor = window.monitor or hl.get_active_monitor()
  if not monitor then
    return
  end

  local target = o.workspaces.workspace_id(monitor, 10)
  if window.workspace and window.workspace.id == target then
    return
  end

  if #hl.get_workspace_windows(tostring(target)) > 0 then
    return
  end

  hl.dispatch(hl.dsp.window.move({
    workspace = tostring(target),
    window = "address:" .. window.address,
    follow = true,
  }))
end)
