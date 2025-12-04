# Permissions s=Guidelines

- Place custom permissions in a `permissions.py` file within the relevant slice or module.
- Each permission is defined as a function which is decorated with the `lib.permissions.permission` decorator
- Permissions typically relate to service layer functions, so their names should reflect the action being performed, e.g., `can_create_user`, `can_delete_post`.
- Each permission function can define whichever parameters are necessary to determine if the action is permitted. Common parameters include:
  - `auth_user`: The authenticated user making the request.
  - `obj`: The object being accessed or modified, if applicable.
  - Additional context-specific parameters as needed.
- All permission functions are async and should return a boolean value: `True` if the action is permitted. They always raise a `lib.errors.AuthorizationError` otherwise.
