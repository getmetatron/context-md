# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When inspecting code across the repository, always verify file existence before using tools like `grep` to avoid spurious errors.
- [2026-07-10] When modifying code based on observed patterns, use programmatic file reading/writing (e.g., Python file I/O) over shell redirection for reliability.
- [2026-07-10] When implementing logic in Django migration routers, ensure a final default return path (`return True`) is present to handle unhandled database/model combinations gracefully.
