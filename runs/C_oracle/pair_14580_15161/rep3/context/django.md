# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In django/db/migrations/serializer.py, each serializer's serialize() returns a (string, imports_set) tuple; any dotted name emitted in the string (e.g. "models.Model") must include a matching import in the imports set, or generated migrations will fail.
- [2026-07-11] When a serializer special-cases a value to a shorthand name, verify the shorthand's namespace is imported; missing import statements in the returned set are a recurring pitfall.
- [2026-07-11] Prefer applying source edits via a Python script that asserts the exact old substring exists before replacing; sed with paths/quotes is error-prone for multi-line or special-character edits.
