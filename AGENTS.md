# Setup responsibilities

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
follow `README.md` and install the custom source assets it identifies. Back up
existing destinations, preserve unrelated settings, and validate the live result
as documented. Do not use the retired comparison/deployment scripts or recreate
a full `.config` snapshot. The experimental GPU update and reboot require a
specific user request for that optional operation.

For PDF support, verify the Zathura PDF plugin and the user's `application/pdf`
association. For LaTeX, verify TeX can find Carlito's style and map files and run
the README's compilation check. A desktop font installation or an existing
generated PDF alone does not establish that the build dependencies are present.
Report failed checks instead of marking the setup complete.
