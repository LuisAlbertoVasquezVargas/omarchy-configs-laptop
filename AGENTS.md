<!-- AGENTS.md -->

# Setup responsibilities

Follow the coding standards in the sibling `../swe-standards` repository:
read its `README.md` and `standards/python.md` before changing Python code.
Use the project's `.venv` environment and maintain root `requirements.txt`.

The repository is being rebuilt incrementally for Omarchy 4.5.0 (Quattro RS).
Implement only the requested configuration in `setup.py`, then let the user
review it before adding the next configuration. Keep code review separate
from applying changes to the live desktop unless the user asks to apply them.
The script takes no command-line arguments. Each installation step skips an
already installed component and prints a message instead of modifying it.
Keep the Agents widget on Omarchy defaults; its step only reports the version.
Use Omarchy 4.5's native ten-workspaces-per-monitor behavior. Preserve its
workspace shortcuts, bar labels, docking, and clamshell handling; do not restore
the retired shared-ten-workspace placement module.
Show all ten workspace buttons using a user-owned widget clone, preserving
native per-monitor numbering and guest-workspace behavior.
The old assets and installer were removed; later README sections are reference
material to revalidate, not proof of compatibility with 4.5.0.

`README.md` describes the desired setup. On the original laptop installation,
the human setup steps through **Zathura**, inclusive, were completed. Preserve
that work, but verify the current state before skipping a step. This completion
history does not apply automatically to a fresh or reinstalled system.

When asked to set up a fresh installation, check every applicable section and
apply missing package and configuration steps. Leave application sign-ins and
personal account synchronization to the user. Skip steps whose documented
checks already pass.

All setup steps after **Zathura**, starting with **LaTeX and Carlito**, are
intended to be automated by agents. When asked to complete the remaining setup,
follow the reviewed steps in `README.md`. Reintroduce custom source assets only
as their configuration steps are reviewed and validated for 4.5.0. Back up
existing destinations, preserve unrelated settings, and validate the live result
as documented. Do not use the retired comparison/deployment scripts or recreate
a full `.config` snapshot. The experimental GPU update and reboot require a
specific user request for that optional operation.

For PDF support, verify the Zathura PDF plugin and the user's `application/pdf`
association. For LaTeX, verify TeX can find Carlito's style and map files. Keep
the README's compilation/viewing check manual; do not build or open sample PDFs
during routine setup runs. Run that check only when requested. A desktop font
installation or an existing generated PDF alone does not establish that the
build dependencies are present.
Report failed checks instead of marking the setup complete.
