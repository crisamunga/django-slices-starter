---
applyTo: '**/services.py, **/services/*.py'
---

Apply the [python coding guidelines](./python.instructions.md) to all code.

# Services Instructions

- Place service layer functions in a `services.py` file within the relevant slice or module.
- Each service function is defined as an async function.
- Service functions should have descriptive names that clearly indicate the action being performed, e.g., `add_user`, `delete_post`.
- Service functions should accept parameters necessary to perform the action, including the authenticated user and any relevant data objects.
- Avoid passing HTTP request or response objects directly to service functions; instead, extract necessary data and pass it as parameters.
- Http layer constructs that may be needed by the service layer (e.g. `session`) should be passed explicitly as parameters, and should be optional whenever possible.
- Services should have a corresponding permission function defined in the `permissions.py` file to handle authorization. (see [Permissions Instructions](./permissions.instructions.md))
- Services that list data from the database should return a queryset and leave it up to the caller to evaluate, paginate or slice it.
- Services that fetch data should include fields for includes, and should use this field to prefetch additional data to reduce database calls.
- Write unit tests for each service function in the corresponding `tests` package, ensuring coverage of all edge cases.

**Example:**

```python
# users/services.py

from uuid import UUID
from django.db.models import Q
from core.models import User
from . import permissions
from lib.errors import not_found_on_error

async def list_users(
    *,
    auth_user: User,
    uuids: list[UUID] | None = None,
    includes: list[str] | None = None,  # any of: roles
    search: str | None = None,
    sort: str | None = None,
) -> "QuerySet[User]":
    await permissions.can_browse_users(user=auth_user)
    queryset = User.objects.all()
    if includes and "roles" in includes:
        queryset = queryset.prefetch_related("roles")
    if includes and "authors" in includes:
        queryset = queryset.prefetch_related("authors")
    if uuids:
        queryset = queryset.filter(uuid__in=uuids)
    if search:
        query = Q()
        query |= Q(email__icontains=search)
        query |= Q(first_name__icontains=search)
        query |= Q(last_name__icontains=search)
        queryset = queryset.filter(query)
    if sort and sort in [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "created_at",
        "-email",
        "-first_name",
        "-last_name",
        "-is_active",
        "-created_at",
    ]:
        queryset = queryset.order_by(sort)
    return queryset


async def add_user(
    *,
    email: str,
    first_name: str,
    last_name: str,
    auth_user: User,
) -> User:
    await permissions.can_add_user(user=auth_user)
    return await User.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )


async def delete_user(*, user_uuid: str | UUID, auth_user: User) -> None:
    with not_found_on_error("User"):
        user = await User.objects.aget(uuid=user_uuid)
    await permissions.can_delete_user(user=auth_user)
    await user.adelete()
```
