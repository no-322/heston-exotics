# heston-exotics

Pricing exotic options under the Heston model.

## Rules

- **I write the core math code myself**: characteristic function, pricers, calibration, Monte Carlo.
  Guide me Socratic-style with questions and hints. Do not write it unless I say "just write it".
- **Boilerplate is fine to write**: plotting, data loading, test scaffolding.
- **Notation**: `v0`, `kappa`, `vbar`, `eta` (vol-of-vol), `rho`.
  `theta` and `xi` are reserved: never use them for Heston params.
- **Explain in short chunks.**
- **Before every commit, review `notes/cheatsheet.md`:**
  - You may fix grammar and improve readability with formatting (lists, `code`, line breaks) and LaTeX for math (e.g. $\rho\eta \ge \kappa$).
  - Keep my wording and voice. Don't rewrite, expand, or add content. It must not read as AI-written.
  - If something is factually wrong, tell me. Only change it after I approve, with minimal modification.
