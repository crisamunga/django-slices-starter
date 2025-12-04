---
applyTo: 'core/**/*.py'
---

Apply the [python coding guidelines](./python.instructions.md) to all code

# Slice Instructions

- This project is organized into slices. Each slice is a self-contained package with its own models, REST API, GraphQL API, etc.
- Each slice should have its own subpackage within the `core` package.
- Each slice includes the following modules:
  - `models.py`: Contains the Django models for the slice.
  - `services.py`: Contains the service layer functions for business logic.
  - `rest.py`: Contains the REST API functions using Django Ninja.
  - `graphql.py`: Contains the GraphQL schema, queries, and mutations for the slice.
  - `permissions.py`: Contains custom permission functions for the slice.
  - `validation.py`: Contains the validation logic for the slice.
  - `tests/`: Package containing unit and integration tests for the slice. Test module names should mirror the main modules and start with a `test_` prefix (e.g., `test_models.py`, `test_services.py`).
- Each slice should be designed to be as independent as possible, minimizing dependencies on other slices.
- Models and APIs need to be registered in the core application to be discovered by Django.
