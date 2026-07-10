# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When using `sed` or file manipulation for code changes, complex conditional logic involving multiple lines can easily lead to syntax errors or unexpected EOF issues, favoring programmatic file reading/writing.
- [2026-07-10] Django's migration system relies heavily on context-aware checks; simply checking `db == 'other'` is insufficient if the router needs to differentiate behavior based on whether a specific model is being considered.
