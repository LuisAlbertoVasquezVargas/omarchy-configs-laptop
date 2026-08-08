# Omarchy Laptop Config

Personal Omarchy configuration for a laptop focused on a single-panel Hyprland workflow, seven persistent workspaces, battery-aware Waybar modules, Ghostty defaults, Steam/Dota 2 window behavior, Intel Vulkan stability, experimental Ferdium integration, and native Linux gaming. It intentionally mirrors `omarchy-configs`; only hardware-specific settings differ. The tracked files under `.config/` are the single source of truth for laptop configuration.

## Target System

- OS: Omarchy
- WM: Hyprland
- GPU: Intel integrated graphics
- Internal display: `eDP-1`, 1920×1200 at 60 Hz
- Optional external display: `HDMI-A-1`
- Waybar includes battery capacity and power-state reporting

## Ghostty Setup

1. Install Ghostty.

   ```bash
   omarchy install terminal ghostty
   ```

2. Make Ghostty the default terminal.

   ```bash
   omarchy default terminal ghostty
   ```

The tracked Ghostty configuration changes the font size from `9` to `13` and disables font-size inheritance so every new window starts at size `13`.

## Setup Steps

1. Update Omarchy immediately after the initial installation and before continuing with any other setup steps. This update is mandatory because the installer may not include all required modules.

   ```bash
   omarchy update
   ```

   Let the update finish, reboot if prompted, and then continue with the remaining steps.

2. Install Brave.

   ```bash
   sudo -v
   yay -S --noconfirm brave-bin
   ```

   After installation, configure Brave:

   1. Open Brave.
   2. Set Brave as the default browser.
   3. Go to **Settings → Search engine** and set:

      - Normal: Google
      - Private: Google

   4. Enable the dark theme under **Settings → Appearance → Theme → Dark**.
   5. Open **Settings → Sync**, start a new Sync chain, choose **Phone/Tablet**, and scan the desktop QR code with Brave on your phone.
   6. Open **Settings → System**, disable **Use graphics acceleration when available**, and relaunch Brave. GPU acceleration can cause issues during long Google Meet video conferences.

3. ~~Install Ferdium.~~

   - ~~`sudo pacman -S --needed --noconfirm flatpak`~~
   - ~~`flatpak install --noninteractive flathub org.ferdium.Ferdium`~~

   ~~Open Ferdium, choose `Use without account`, add the messaging services you need, and scan the QR code for WhatsApp.~~

   This step is temporarily disabled while investigating whether Ferdium contributes to the GPU instability.

4. Install and activate the latest Node.js through `mise`, then update npm.

   ```bash
   mise use --global node@latest
   npm install -g npm@latest
   ```

5. Install the latest OpenAI Codex CLI and verify the environment.

   ```bash
   npm install -g @openai/codex@latest
   node -v
   npm -v
   codex --version
   ```

6. Authenticate GitHub CLI.

   ```bash
   gh auth login
   ```

   Use browser login when prompted.

7. ~~Add the Git push alias.~~

   - ~~`echo 'alias gpm="git push origin main"' >> ~/.bashrc`~~
   - ~~`source ~/.bashrc`~~

   This alias is currently unused because Git operations are being handled through Codex.

8. Clone this repository.

   ```bash
   cd ~/Projects
   git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop.git
   cd omarchy-configs-laptop
   ```

9. Compare the repository configs with the current system configs.

   ```bash
   python scripts/compare_configs.py
   ```

10. Apply the repository configs.

   ```bash
   python scripts/apply_configs.py
   ```

   The script previews creates/replacements first and only writes after you type `yes`. Replaced files are backed up under `~/.local/state/omarchy-configs/backups/`.

11. Compare again to confirm the files now match.

    ```bash
    python scripts/compare_configs.py
    ```

12. Reload the desktop.

    ```bash
    hyprctl reload
    omarchy restart waybar
    ```

    Reopen Ghostty windows so font, padding, and keyboard changes are picked up. Reboot if you want to verify the full autostart flow from a clean login.

13. Install the optional Ghost Pastel Omarchy theme.

    ```bash
    omarchy-theme-install https://github.com/row-huh/omarchy-ghost-pastel-theme
    ```

    Theme page: `https://omarchytheme.com/themes/ghost-pastel/`

14. Install Steam.

    ```bash
    sudo pacman -S --needed --noconfirm steam
    ```

15. Configure Dota 2.

    Use the native Linux build with Vulkan. Do not use Gamescope, Proton, Wine, or wrappers because they can break VAC verification and disable matchmaking.

    Steam launch options:

    ```bash
    SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 %command% -console -novid
    ```

16. Configure Left 4 Dead 2.

    Force X11 to avoid broken input scaling under Wayland.

    Steam launch options:

    ```bash
    SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=pulse %command% -console -novid
    ```

    If Waybar appears over the game, toggle real fullscreen with `SUPER + F`.

17. Configure StarCraft: Remastered.

    Download the Battle.net Windows installer from `https://www.blizzard.com/download`, add it to Steam as a non-Steam game, force Proton Experimental, run the installer, log in to Battle.net, and install StarCraft: Remastered while keeping the Battle.net window visible.

    Steam launch options:

    ```bash
    PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 %command%
    ```

## Neovim Configuration

The tracked Neovim overrides show hidden files in Neo-tree by default and render standalone images and inline Markdown images through Ghostty's graphics-protocol support. PDF documents remain external and open in Zathura.

1. Confirm Ghostty is the default terminal and start Neovim from a fresh Ghostty window.

2. Install the image conversion and PDF preview dependencies.

   ```bash
   omarchy pkg add imagemagick zathura zathura-pdf-mupdf
   xdg-mime default org.pwmt.zathura.desktop application/pdf
   xdg-mime query default application/pdf
   ```

   The final command should print `org.pwmt.zathura.desktop`, confirming that PDFs open with Zathura by default.

3. Apply the repository configs to install the tracked Neo-tree and image-rendering overrides.

4. Restart Neovim and run `:checkhealth snacks`. Ghostty and ImageMagick should pass the image checks when Neovim is running interactively inside Ghostty.

5. Test a standalone PNG or JPEG, then open a Markdown document containing a relative image reference. Use Zathura for PDF previews rather than rendering PDFs inline.

Headless Neovim cannot complete the terminal graphics handshake, so its health check may incorrectly report that the graphics protocol is unavailable. Validate rendering in an interactive Ghostty window.

## Experimental: Codex Workspace Shortcut

These shortcuts open Codex and a terminal in the corresponding project workspace:

- `SUPER + HOME` uses workspace 2 and `~/Projects/MOVER-research-materials/`.
- `SUPER + END` uses workspace 3 and `~/Projects/shopping-list-ui/`.

Add the following lines to `~/.config/hypr/bindings.conf`. They are intentionally kept out of the tracked Hyprland configuration while they are being evaluated:

```text
bindd = SUPER, HOME, Codex + terminal (workspace 2), workspace, 2
bind = SUPER, HOME, exec, [workspace 2 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/MOVER-research-materials/" && exec codex'
bind = SUPER, HOME, exec, [workspace 2 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/MOVER-research-materials/" && exec bash'
bindd = SUPER, END, Codex + terminal (workspace 3), workspace, 3
bind = SUPER, END, exec, [workspace 3 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/shopping-list-ui/" && exec codex'
bind = SUPER, END, exec, [workspace 3 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/shopping-list-ui/" && exec bash'
```

## Laptop display presets

The tracked monitor file defaults to the internal `eDP-1` panel. It also keeps
disabled presets for classroom mirroring, the Sala 90 extended display, and a
4K mirrored display. Confirm connector names with `hyprctl monitors` before
enabling one preset, and enable only one layout at a time.
