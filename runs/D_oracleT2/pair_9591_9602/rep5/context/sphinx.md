# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When inspecting object signatures, always check for descriptor/property handling paths (`__get__`) to ensure type annotations are captured correctly, as direct inspection might miss underlying function details.
- [2026-07-10] When modifying Sphinx nodes, always validate the existence and structure of context nodes (like `signature`) before attempting to access attributes like `module` or `fullname` to prevent `KeyError` exceptions.
- [2026-07-10] When dealing with environment state across multiple functions, use `app.env.temp_data.get(key, {})` pattern to safely retrieve and initialize complex structures like annotation dictionaries.
