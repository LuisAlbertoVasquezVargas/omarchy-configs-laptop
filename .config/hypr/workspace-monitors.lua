-- Model-specific workspace placement, reapplied on monitor changes.
local benq_description = "BNQ BenQ G610HDAL A5B03247019"
local rules, previous_layout = {}, nil

local function reconcile(move_existing)
  local internal, external, benq
  for _, monitor in ipairs(hl.get_monitors()) do
    if monitor.name == "eDP-1" then
      internal = monitor.name
    else
      external = external or monitor.name
      if monitor.description == benq_description then benq = monitor.name end
    end
  end
  external = benq or external
  if not internal and not external then return end

  local targets, defaults = {}, {}
  for id = 1, 10 do
    if not internal then
      targets[id] = external
      defaults[id] = id == 1
    elseif benq then
      targets[id] = id >= 8 and benq or internal
      defaults[id] = id == 1 or id == 8
    elseif external then
      -- Preserve the existing split for other external monitors.
      targets[id] = id == 7 and external or internal
      defaults[id] = id == 1 or id == 7
    else
      targets[id] = internal
      defaults[id] = id == 1
    end
  end

  local layout = table.concat(targets, ",")
  if layout ~= previous_layout then
    for _, rule in ipairs(rules) do rule:set_enabled(false) end
    rules = {}
    for id = 1, 10 do
      rules[id] = hl.workspace_rule({
        workspace = tostring(id), monitor = targets[id],
        persistent = true, default = defaults[id],
      })
    end
    previous_layout = layout
  end

  if move_existing then
    for _, workspace in ipairs(hl.get_workspaces()) do
      local target = targets[workspace.id]
      if target and workspace.monitor and workspace.monitor.name ~= target then
        hl.dispatch(hl.dsp.workspace.move({ workspace = tostring(workspace.id), monitor = target }))
      end
    end
  end
end

reconcile(false)
hl.on("config.reloaded", function() reconcile(true) end)
hl.on("monitor.layout_changed", function() reconcile(true) end)
hl.on("monitor.added", function() reconcile(true) end)
hl.on("monitor.removed", function() reconcile(true) end)
