# setup.py

from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import tomlkit

THEME_NAME = "Ghost Pastel"
THEME_URL = "https://github.com/row-huh/omarchy-ghost-pastel-theme"

def omarchy_output(*arguments):
    result = subprocess.run(
        ["omarchy", *arguments],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout.strip()

def install_ghost_pastel():
    installed_themes = omarchy_output("theme", "list").splitlines()

    if THEME_NAME in installed_themes:
        print("Ghost Pastel is already installed; skipping.")
        return

    print("Installing Ghost Pastel...", flush=True)
    subprocess.run(["omarchy", "theme", "install", THEME_URL], check=True)

    if THEME_NAME not in omarchy_output("theme", "list").splitlines():
        raise RuntimeError("Ghost Pastel was not found after installation.")

    print("Ghost Pastel installed.")

def install_brave():
    if shutil.which("brave") is not None:
        print("Brave is already installed; skipping.")
        return

    print("Installing Brave...", flush=True)
    subprocess.run(["omarchy", "install", "browser", "brave"], check=True)

    if shutil.which("brave") is None:
        raise RuntimeError("Brave was not found after installation.")

    print("Brave installed.")

def set_brave_default():
    current_default = omarchy_output("default", "browser")
    if current_default == "brave":
        print("Brave is already the default browser; skipping.")
        return

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    mime_settings = config_directory / "mimeapps.list"
    backup = None
    if mime_settings.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = mime_settings.with_name(f"mimeapps.list.backup-{timestamp}")
        shutil.copy2(mime_settings, backup)
        print(f"MIME settings backed up to {backup}", flush=True)

    config_directory.mkdir(parents=True, exist_ok=True)
    print("Setting Brave as the default browser...", flush=True)
    try:
        subprocess.run(["omarchy", "default", "browser", "brave"], check=True)
        if omarchy_output("default", "browser") != "brave":
            raise RuntimeError("Brave is not the default browser after configuration.")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        if backup is None:
            mime_settings.unlink(missing_ok=True)
        else:
            shutil.copy2(backup, mime_settings)
        raise

    print("Brave set as the default browser.")

def report_whatsapp():
    current_version = omarchy_output("version")
    print(f"WhatsApp already installed in version {current_version}")

def configure_whatsapp_workspace():
    configure_hyprland_override("hyprland.lua", "whatsapp-workspace.lua", "WhatsApp workspace placement")

def report_slack():
    print("Slack can be installed as a service.")

def report_discord():
    current_version = omarchy_output("version")
    print(f"Discord already installed in version {current_version}")

def install_zathura():
    required_packages = ["zathura", "zathura-pdf-mupdf", "xdg-utils"]
    installed_packages = subprocess.check_output(["pacman", "-Qq"], text=True).splitlines()
    missing_packages = [package for package in required_packages if package not in installed_packages]

    if missing_packages:
        print(f"Installing Zathura dependencies: {', '.join(missing_packages)}...", flush=True)
        subprocess.run(["omarchy", "pkg", "add", *missing_packages], check=True)
    else:
        print("Zathura packages are already installed; skipping installation.")

    version = subprocess.check_output(["zathura", "--version"], text=True, stderr=subprocess.STDOUT)
    if "pdf-mupdf" not in version:
        raise RuntimeError("Zathura's pdf-mupdf plugin is not available.")

def set_zathura_pdf_default():
    desktop_id = "org.pwmt.zathura.desktop"
    current_default = subprocess.check_output(
        ["xdg-mime", "query", "default", "application/pdf"], text=True
    ).strip()

    if current_default == desktop_id:
        print("Zathura is already the default PDF reader; skipping.")
        return

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    mime_settings = config_directory / "mimeapps.list"
    if mime_settings.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = mime_settings.with_name(f"mimeapps.list.backup-{timestamp}")
        shutil.copy2(mime_settings, backup)
        print(f"MIME settings backed up to {backup}", flush=True)

    config_directory.mkdir(parents=True, exist_ok=True)
    subprocess.run(["xdg-mime", "default", desktop_id, "application/pdf"], check=True)
    current_default = subprocess.check_output(
        ["xdg-mime", "query", "default", "application/pdf"], text=True
    ).strip()

    if current_default != desktop_id:
        raise RuntimeError("Zathura is not the default PDF reader after configuration.")

    print("Zathura set as the default PDF reader.")

def install_latex_and_carlito():
    required_packages = [
        "texlive-binextra",
        "texlive-latexrecommended",
        "texlive-latexextra",
        "texlive-fontsrecommended",
        "texlive-fontsextra",
        "texlive-pictures",
        "texlive-langportuguese",
        "poppler",
    ]
    installed_packages = subprocess.check_output(["pacman", "-Qq"], text=True).splitlines()
    missing_packages = [package for package in required_packages if package not in installed_packages]

    if missing_packages:
        print(f"Installing LaTeX dependencies: {', '.join(missing_packages)}...", flush=True)
        subprocess.run(["omarchy", "pkg", "add", *missing_packages], check=True)
    else:
        print("LaTeX packages are already installed; skipping installation.")

    for tool in ["latexmk", "pdflatex", "pdffonts", "kpsewhich"]:
        if shutil.which(tool) is None:
            raise RuntimeError(f"Required LaTeX tool was not found: {tool}")

    for tex_file in ["beamer.cls", "carlito.sty", "carlito.map", "mweights.sty"]:
        location = subprocess.check_output(["kpsewhich", tex_file], text=True).strip()
        if not location:
            raise RuntimeError(f"TeX could not find {tex_file}")

    print("LaTeX tools and Carlito support files verified.")

def reload_hyprland(label):
    try:
        subprocess.check_output(["hyprctl", "reload"], text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        details = error.output.strip() or str(error)
        raise RuntimeError(f"{label}: Hyprland reload failed: {details}") from error
    errors = subprocess.check_output(["hyprctl", "configerrors"], text=True).strip()
    if errors:
        raise RuntimeError(f"{label}: Hyprland configuration errors: {errors}")
    print(f"{label}: Hyprland reloaded; no configuration errors.", flush=True)

def touchpad_uses_clickfinger():
    output = subprocess.check_output(
        ["hyprctl", "-j", "getoption", "input:touchpad:clickfinger_behavior"], text=True
    )
    option = json.loads(output)
    if not isinstance(option.get("bool"), bool):
        raise RuntimeError("Hyprland did not report a boolean touchpad click setting.")
    return option["bool"]

def configure_touchpad_right_click():
    reload_hyprland("Touchpad settings check")
    if not touchpad_uses_clickfinger():
        print("Touchpad lower-right click is already configured; skipping.")
        return

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    input_file = config_directory / "hypr/input.lua"
    original = input_file.read_text()
    override = """hl.config({
  input = {
    touchpad = {
      clickfinger_behavior = false,
    },
  },
})
"""
    updated = original.rstrip() + "\n\n" + override
    subprocess.run(["luac", "-p", "-"], input=updated, text=True, check=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = input_file.with_name(f"input.lua.backup-{timestamp}")
    shutil.copy2(input_file, backup)
    print(f"Input settings backed up to {backup}", flush=True)

    try:
        input_file.write_text(updated)
        reload_hyprland("Touchpad settings update")
        if touchpad_uses_clickfinger():
            raise RuntimeError("Touchpad lower-right click did not take effect.")
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError):
        shutil.copy2(backup, input_file)
        reload_hyprland("Touchpad settings restore")
        raise

    print("Touchpad lower-right click configured.")

def configure_neovim_plugin(filename, specification, label):
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    plugin_file = config_directory / "nvim/lua/plugins" / filename
    original = plugin_file.read_text() if plugin_file.exists() else ""

    if original.rstrip().endswith(specification.rstrip()):
        print(f"{label} is already configured; skipping.")
        return

    preserved_specs = f"  (function(...)\n{original}\n  end)(...),\n" if original.strip() else ""
    header = f"-- nvim/lua/plugins/{filename}\n\nreturn {{\n"
    updated = header + preserved_specs + specification
    subprocess.run(["luac", "-p", "-"], input=updated, text=True, check=True)

    if plugin_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = plugin_file.with_name(f"{filename}.backup-{timestamp}")
        shutil.copy2(plugin_file, backup)
        print(f"{label} settings backed up to {backup}", flush=True)

    plugin_file.parent.mkdir(parents=True, exist_ok=True)
    plugin_file.write_text(updated)
    print(f"{label} configured. Restart Neovim to apply.")

def configure_neo_tree():
    specification = """  {
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
"""

    configure_neovim_plugin("neo-tree.lua", specification, "Neo-tree visibility")

def configure_image_rendering():
    if shutil.which("magick") is None:
        print("Installing ImageMagick for image rendering...", flush=True)
        subprocess.run(["omarchy", "pkg", "add", "imagemagick"], check=True)
        if shutil.which("magick") is None:
            raise RuntimeError("ImageMagick was not found after installation.")
    else:
        print("ImageMagick is already installed; skipping installation.")

    specification = """  {
    "folke/snacks.nvim",
    opts = {
      image = {
        enabled = true,
      },
    },
  },
}
"""
    configure_neovim_plugin("image-rendering.lua", specification, "Snacks image rendering")

def configure_codex_defaults():
    if shutil.which("codex") is None:
        raise RuntimeError("Install the Codex CLI before configuring its defaults.")

    config_directory = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    config_file = config_directory / "config.toml"
    original = config_file.read_text() if config_file.exists() else "# config.toml\n\n"
    try:
        configuration = tomlkit.parse(original)
    except tomlkit.exceptions.ParseError as error:
        raise RuntimeError(f"Invalid Codex configuration: {error}") from error

    defaults = {
        "approval_policy": "on-request",
        "approvals_reviewer": "auto_review",
        "sandbox_mode": "workspace-write",
    }
    if all(configuration.get(key) == value for key, value in defaults.items()):
        print("Codex approval defaults are already configured; skipping.")
        return

    for key, value in defaults.items():
        configuration[key] = value

    backup = None
    if config_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = config_file.with_name(f"config.toml.backup-{timestamp}")
        shutil.copy2(config_file, backup)
        print(f"Codex settings backed up to {backup}", flush=True)

    config_directory.mkdir(parents=True, exist_ok=True)
    try:
        config_file.write_text(tomlkit.dumps(configuration), encoding="utf-8")
        subprocess.run(["codex", "features", "list"], stdout=subprocess.DEVNULL, check=True)
    except (OSError, subprocess.CalledProcessError):
        if backup is None:
            config_file.unlink(missing_ok=True)
        else:
            shutil.copy2(backup, config_file)
        raise

    print("Codex approval defaults configured. Start a new Codex session to apply.")

def install_steam():
    if shutil.which("steam") is not None:
        print("Steam is already installed; skipping.")
        return

    print("Installing Steam...", flush=True)
    subprocess.run(["omarchy", "install", "gaming", "steam"], check=True)

    if shutil.which("steam") is None:
        raise RuntimeError("Steam was not found after installation.")

    print("Steam installed.")

def configure_bar_widget(widget_id, default_section, settings, label):
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    config_file = (config_directory / "omarchy/shell.json").resolve()
    configuration = json.loads(config_file.read_text()) if config_file.exists() else {}
    if not isinstance(configuration, dict):
        raise RuntimeError("Omarchy shell configuration must be a JSON object.")

    bar = configuration.setdefault("bar", {})
    if not isinstance(bar, dict):
        raise RuntimeError("Omarchy bar configuration must be a JSON object.")
    if "layout" not in bar:
        omarchy_directory = Path(os.environ.get("OMARCHY_PATH") or "/usr/share/omarchy")
        defaults = json.loads((omarchy_directory / "config/omarchy/shell.json").read_text())
        bar["layout"] = defaults["bar"]["layout"]

    layout = bar["layout"]
    if not isinstance(layout, dict):
        raise RuntimeError("Omarchy bar layout must be a JSON object.")
    matches = []
    legacy_id = "lvasquez." + widget_id.removeprefix("omarchy.")
    for section in ["left", "centerBegin", "center", "centerEnd", "right", "tray"]:
        entries = layout.get(section, [])
        if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
            raise RuntimeError(f"Invalid Omarchy bar section: {section}")
        matches.extend(entry for entry in entries if entry.get("id") in [widget_id, legacy_id])
    if len(matches) > 1:
        raise RuntimeError(f"Multiple entries found for {widget_id}; resolve the duplicate entries first.")
    if matches:
        widget = matches[0]
    else:
        widget = {"id": widget_id}
        layout.setdefault(default_section, []).append(widget)

    if all(widget.get(key) == value and type(widget.get(key)) is type(value) for key, value in settings.items()):
        print(f"{label} is already configured; skipping.")
        return
    widget.update(settings)

    if config_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = config_file.with_name(f"shell.json.backup-{timestamp}")
        shutil.copy2(config_file, backup)
        print(f"Shell settings backed up to {backup}", flush=True)

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=config_file.parent, prefix=".shell-", suffix=".tmp", delete=False
    ) as temporary:
        temporary.write(json.dumps(configuration, ensure_ascii=False, indent=2) + "\n")
        temporary_file = Path(temporary.name)
    try:
        if config_file.exists():
            shutil.copymode(config_file, temporary_file)
        temporary_file.replace(config_file)
    finally:
        temporary_file.unlink(missing_ok=True)

    print(f"{label} configured. Check the bar; the shell reloads automatically.")

def configure_clock_format():
    formats = {
        "format": "dd MMM ddd · 'W'ww · HH:mm",
        "formatAlt": "dd MMM ddd · 'W'ww · HH:mm",
        "verticalFormat": "HH\n—\nmm",
    }
    configure_bar_widget("omarchy.clock", "center", formats, "Clock format")

def configure_battery_percentage():
    configure_bar_widget("omarchy.power", "right", {"showPercentage": True}, "Battery percentage")

def configure_cloned_qml_widget(source_id, old_code, new_code, label, test_filename=None):
    username = os.environ.get("USER") or subprocess.check_output(["id", "-un"], text=True).strip()
    plugin_id = f"{username}.{source_id.removeprefix('omarchy.')}"
    config_directory = Path.home() / ".config/omarchy"
    plugin_directory = config_directory / "plugins" / plugin_id
    shell_file = config_directory / "shell.json"
    plugin_existed = plugin_directory.exists() or plugin_directory.is_symlink()
    shell_existed = shell_file.exists()

    if plugin_existed:
        manifest = json.loads((plugin_directory / "manifest.json").read_text())
        if manifest.get("id") != plugin_id or manifest.get("omarchy", {}).get("clonedFrom") != source_id:
            raise RuntimeError(f"{plugin_directory} is not a clone of {source_id}.")
        filename = manifest["entryPoints"]["barWidget"]
        widget_file = plugin_directory / filename
        if widget_file.is_symlink() or not widget_file.resolve().is_relative_to(plugin_directory.resolve()):
            raise RuntimeError("The widget must be a regular file inside its clone.")
    else:
        catalog = json.loads(omarchy_output("plugin", "catalog"))
        source = next((plugin for plugin in catalog if plugin["id"] == source_id and plugin["firstParty"]), None)
        if source is None:
            raise RuntimeError(f"Built-in widget not found: {source_id}")
        manifest = json.loads(Path(source["manifestPath"]).read_text())
        filename = manifest["entryPoints"]["barWidget"]
        widget_file = Path(source["barWidgetPath"])

    original = widget_file.read_text()
    if original.count(old_code) + original.count(new_code) != 1:
        raise RuntimeError(f"{label} implementation changed; review the widget before applying this step.")
    updated = original.replace(old_code, new_code, 1)

    shell_settings = json.loads(shell_file.read_text()) if shell_existed else {}
    layout = shell_settings.get("bar", {}).get("layout", {})
    active_ids = {entry["id"] for entries in layout.values() for entry in entries}
    expected_id = plugin_id if plugin_existed else source_id
    if original == updated and expected_id in active_ids:
        print(f"{label} is already configured; skipping.")
        return

    with tempfile.TemporaryDirectory(prefix="widget-check-") as temporary:
        staged_widget = Path(temporary) / Path(filename).name
        staged_widget.write_text(updated)
        subprocess.run(
            ["/usr/lib/qt6/bin/qmlformat", "--ignore-settings", str(staged_widget)],
            stdout=subprocess.DEVNULL,
            check=True,
        )
        if test_filename:
            test_file = Path(__file__).resolve().parent / "tests" / test_filename
            try:
                subprocess.check_output(
                    ["node", str(test_file)],
                    env=dict(os.environ, WIDGET_QML_PATH=str(staged_widget)),
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            except subprocess.CalledProcessError as error:
                raise RuntimeError(f"{label} checks failed:\n{error.output}") from error

    state_directory = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_directory = state_directory / "omarchy/backups" / f"{source_id.removeprefix('omarchy.')}-widget-{timestamp}"
    backup_directory.mkdir(parents=True)
    if shell_existed:
        shutil.copy2(shell_file, backup_directory / "shell.json")
    if plugin_existed:
        shutil.copy2(widget_file, backup_directory / Path(filename).name)
    print(f"{label} backups saved to {backup_directory}", flush=True)

    try:
        if not plugin_existed:
            subprocess.run(["omarchy", "plugin", "clone", source_id], check=True)
        widget_file = plugin_directory / filename
        widget_file.write_text(updated)
        if plugin_existed and plugin_id not in active_ids:
            subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
        subprocess.run(["omarchy", "restart", "shell"], check=True)
    except (OSError, subprocess.CalledProcessError):
        if shell_existed:
            shutil.copy2(backup_directory / "shell.json", shell_file)
        else:
            shell_file.unlink(missing_ok=True)
        if plugin_existed:
            shutil.copy2(backup_directory / Path(filename).name, widget_file)
        elif plugin_directory.is_dir():
            shutil.rmtree(plugin_directory)
        subprocess.run(["omarchy", "restart", "shell"], check=False)
        raise

    print(f"{label} configured.")

def configure_battery_panel_refresh():
    old_timer = "Timer { interval: 5000; running: root.opened; repeat: true; onTriggered: root.refresh() }"
    new_timer = "Timer { interval: 2000; running: root.opened; repeat: true; onTriggered: root.refresh() }"
    configure_cloned_qml_widget("omarchy.power", old_timer, new_timer, "Battery panel refresh (2 seconds)")

def configure_workspace_buttons():
    old_code = """  // The first five of the monitor's own, and any of the rest that exist. After
  // them come workspaces that are only visiting: those of a monitor that is
  // unplugged, which had no room to join this one's.
  function workspaceIds() {
    var base = root.block * root.slots
    var ids = [base + 1, base + 2, base + 3, base + 4, base + 5]
"""
    new_code = """  function workspaceIds() {
    var base = root.block * root.slots
    var ids = []
    for (var slot = 1; slot <= root.slots; slot++) ids.push(base + slot)
"""
    configure_cloned_qml_widget(
        "omarchy.workspaces", old_code, new_code, "Ten workspace buttons per monitor", "workspace-buttons.test.cjs"
    )

def configure_charging_icon():
    username = os.environ.get("USER") or subprocess.check_output(["id", "-un"], text=True).strip()
    plugin_id = f"{username}.power"
    plugin_directory = Path.home() / ".config/omarchy/plugins" / plugin_id
    manifest = json.loads((plugin_directory / "manifest.json").read_text())
    if manifest.get("id") != plugin_id or manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.power":
        raise RuntimeError(f"{plugin_directory} is not a clone of omarchy.power.")

    model_file = plugin_directory / "Model.js"
    if model_file.is_symlink():
        raise RuntimeError("The power model must be a regular cloned file.")
    original = model_file.read_text()
    old_rule = """  if (d.state === s.FullyCharged && fraction < 0.99) return true
  if (d.state !== s.Charging || fraction >= 0.99) return false

  return Number(d.changeRate || 0) <= 0.2 || Number(d.timeToFull || 0) >= 8 * 60 * 60
"""
    new_rule = """  if (d.state === s.FullyCharged && fraction < 0.99) return true
  return false
"""
    if original.count(new_rule) == 1 and old_rule not in original:
        print("Battery charging icon is already configured; skipping.")
        return
    if original.count(old_rule) != 1:
        raise RuntimeError("Power charge-hold logic changed; review the model before applying this step.")
    updated = original.replace(old_rule, new_rule, 1)

    if shutil.which("node") is None:
        raise RuntimeError("Node.js is required to verify the power model.")
    test_file = Path(__file__).resolve().parent / "tests/power-model.test.cjs"
    with tempfile.TemporaryDirectory(prefix="power-model-check-") as temporary:
        staged_model = Path(temporary) / "Model.js"
        staged_model.write_text(updated)
        subprocess.run(
            ["node", str(test_file)],
            env=dict(os.environ, POWER_MODEL_PATH=str(staged_model)),
            check=True,
        )

    state_directory = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_directory = state_directory / "omarchy/backups" / f"charging-icon-{timestamp}"
    backup_directory.mkdir(parents=True)
    backup = backup_directory / "Model.js"
    shutil.copy2(model_file, backup)
    print(f"Power model backed up to {backup}", flush=True)

    try:
        model_file.write_text(updated)
        subprocess.run(["omarchy", "restart", "shell"], check=True)
    except (OSError, subprocess.CalledProcessError):
        shutil.copy2(backup, model_file)
        subprocess.run(["omarchy", "restart", "shell"], check=False)
        raise

    print("Battery charging icon configured. Verify it by unplugging and reconnecting the charger.")

def report_agents_widget():
    current_version = omarchy_output("version")
    print(f"Using default Agents widget from Omarchy version {current_version}")

def configure_hyprland_override(filename, source_name, label):
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    config_file = config_directory / "hypr" / filename
    source_file = Path(__file__).resolve().parent / "config/hypr" / source_name
    override = source_file.read_text()
    original = config_file.read_text()

    reload_hyprland(f"{label} check")
    if original.rstrip().endswith(override.rstrip()):
        print(f"{label} is already configured; skipping.")
        return

    updated = original.rstrip() + "\n\n" + override
    subprocess.run(["luac", "-p", "-"], input=updated, text=True, check=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = config_file.with_name(f"{filename}.backup-{timestamp}")
    shutil.copy2(config_file, backup)
    print(f"{label} settings backed up to {backup}", flush=True)

    try:
        config_file.write_text(updated)
        reload_hyprland(f"{label} update")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        shutil.copy2(backup, config_file)
        reload_hyprland(f"{label} restore")
        raise

    print(f"{label} configured.")

def configure_compact_layout():
    configure_hyprland_override("looknfeel.lua", "compact-layout.lua", "Compact layout and theme borders")

def configure_displays():
    configure_hyprland_override("monitors.lua", "displays.lua", "Laptop and external display profiles")

def report_monitor_workspaces():
    current_version = omarchy_output("version")
    print(f"Using native Omarchy workspace behavior: 10 workspaces per monitor in version {current_version}")

def main():
    if len(sys.argv) > 1:
        raise RuntimeError("This script takes no arguments. Run: python setup.py")

    if shutil.which("omarchy") is None:
        raise RuntimeError("Run this script on an Omarchy desktop.")

    install_ghost_pastel()
    install_brave()
    set_brave_default()
    report_whatsapp()
    configure_whatsapp_workspace()
    report_slack()
    report_discord()
    install_zathura()
    set_zathura_pdf_default()
    install_latex_and_carlito()
    configure_touchpad_right_click()
    configure_neo_tree()
    configure_image_rendering()
    configure_codex_defaults()
    install_steam()
    configure_clock_format()
    configure_battery_percentage()
    configure_battery_panel_refresh()
    configure_charging_icon()
    report_agents_widget()
    configure_compact_layout()
    configure_displays()
    configure_workspace_buttons()
    report_monitor_workspaces()

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
