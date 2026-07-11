# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] The `@deconstructible` decorator from `django.utils.deconstruct` accepts a `path=` kwarg to set the deconstructed import path; public classes in `django/db/models/expressions.py` use `path='django.db.models.<Name>'` matching their re-export in `django/db/models/__init__.py`.
- [2026-07-11] Don't add `@deconstructible` to classes only used as base classes (e.g. Expression, Subquery/Exists, Window/WindowFrame); apply it to the concrete public expression classes that are themselves deconstructed.
- [2026-07-11] BSD `sed -i` (macOS) requires an empty extension argument: use `sed -i '' 'Nd' file`, not the GNU `sed -i 'Nd' file` form.
