# Validators Guidelines

- Place custom validators in a `validators.py` file within the relevant slice or module.
- Each validator extends `lib.validation.ValidationRule` and implements the `__call__` method.
- The name of the validator should clearly indicate what it validates e.g. `EmailShouldBeUnique`, `PasswordShouldBeStrong`.
- The call method always receives these parameters:
  - `value`: The value to be validated.
  - `obj`: The object containing the whole input data, useful for cross-field validation.
  - `auth_user`: The authenticated user making the request, useful for permission-based validation.
  - `path`: The path to the value within the input data, useful for error reporting.
- Validators should raise `lib.errors.InputError` with a descriptive message when validation fails.
- Use existing validators from `lib.validation` as much as possible to maintain consistency.
- Write unit tests for each validator in the corresponding `tests` package, ensuring coverage of all edge cases.

**Example:**

```python
# posts/validators.py
class PostAuthorsShouldExist(base.ValidationRule):
    async def __call__(self, *, value: "list[PostAuthorInput]", path: list[str | int], **kwargs: Any) -> None:
        if not value:
            return

        errors = []

        author_uuids = [author.author_uuid for author in value]
        existing = set(await alist(User.objects.filter(uuid__in=author_uuids).values_list("uuid", flat=True)))

        for i, author in enumerate(value):
            if author.author_uuid not in existing:
                errors += [
                    InputError(
                        f"Author with UUID {author.author_uuid} does not exist",
                        code="author_not_found",
                        message=_("Author with UUID {uuid} not found.") % { "uuid": author.author_uuid },
                        path=path + [i, "author_uuid"],
                    )
                ]

        if errors:
            raise ExceptionGroup("Some authors were not found", errors)
```
