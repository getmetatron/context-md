# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core framework files like `django/db/migrations/writer.py`, relying solely on file content checks (like `if "import" not in content`) is insufficient; structural analysis or targeted code replacement is necessary.
- [2026-07-10] Repeated attempts to use shell commands (`sed`) within Python execution blocks or directly in the shell require careful escaping and understanding of the shell's parsing rules.
- [2026-07-10] When dealing with dependency management in code, the required import should be added to the appropriate scope (e.g., the `special_cases` list in `serializer.py`) rather than just appending it to the file end.
