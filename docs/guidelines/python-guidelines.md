# General Python Guidelines

- Adhere to PEP 8 style guidelines for Python code especially regarding naming conventions.
- Dependency and environment management is done using uv
- Code style is enforced and formatted using ruff.
- Type checking is done using mypy.
- Include type annotations for all function signatures and class attributes.
- Prefer async functions when dealing with I/O operations like database access or network calls.
- Prefer to use keyword arguments over positional arguments when writing function definitions and calls, especially when there are more than one parameter.
- Prefer using named tuples or dataclasses for grouping related data instead of tuples and dictionaries.
- When ignoring a type-checking or linting rule, indicate the reason why it's being ignored.
- When raising errors, you should extend `lib.errors.BaseError` or one of it's subclasses to provide more context to the caller. Otherwise it will be wrapped into a generic server error once it gets to the response.
