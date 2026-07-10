# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When using `grep` across a repository, be mindful of shell syntax limitations; complex patterns like balanced brackets can cause immediate failures.
- [2026-07-09] File path discovery for modules like `optimizer.py` requires checking multiple locations (`ls -R`, `grep -r`) as the file's existence or location is not guaranteed.
- [2026-07-09] Modifying code via scripting (e.g., `python3 - <<'EOF'`) requires careful regex construction to handle multi-line context and potential class/method boundaries.
