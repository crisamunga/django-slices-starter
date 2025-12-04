---
applyTo: '**/*.py'
---

- Apply the [python coding guidelines](./../../docs/guidelines/python-guidelines.md) to all code.

- You don't have to fiddle with sorting imports or formatting code manually. Saving the file will automatically format it.
- Since ruff and mypy are used, you can safely ignore these errors in generated code:
  - Unsorted imports
  - Unused imports
  - No newline at end of file
