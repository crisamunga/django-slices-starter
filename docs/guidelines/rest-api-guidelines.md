Apply the [python coding guidelines](./python.instructions.md) to all code.

# Guidelines for authoring rest apis

- This project uses [Django Ninja](https://django-ninja.rest-framework.com/) for building REST APIs. Follow its conventions and best practices.

## Router definition

- The router declaration should be at the top of the file after imports.
- The router variable should always be named `router`.
- All API endpoints should be defined in `rest.py` files or as modules within a `rest` package, and imported into the main router in `core/rest/api.py`.
- When being added to the main router, the path parameter should be an empty string `""` to avoid path duplication.
- All endpoints in the rest api files should have the full path specified as the path parameter, but should not start with a leading slash `/`. e.g. `"users/{user_id}/"`.
- The following additional parameters should also be set when routes to the api endpoint router decorator:
  - `tags`: A list of strings representing the tags for the endpoint.
  - `summary`: Should be set to `<resource> | <action>`, e.g., `profile | browse`.
  - `responses`: Should be set based on a helper function imported from lib.rest with the success status code and the response schema. e.g. `response(200, Profile)`. Responses that do not return any content should use `response(204)`.
  - `url_name`: Should be set to `<resource>-<action>`, e.g., `profile-browse`.
  - `operation_id`: Should be set to the same value as url_name, e.g., `profile-browse`.
- In addition to the router decorator, a `log_error()` decorator should also be applied to each endpoint to log errors.
- Use async functions for all endpoint handlers.
- Use type hints for all function parameters and return types.
- All request and response types should subclass `Schema` from `ninja`.
- All endpoint functions should be named one of the verbs from the following list, based on the action being performed:
  - `browse`
  - `read`
  - `add`
  - `add_many`
  - `edit`
  - `edit_many`
  - `delete`
  - `delete_many`

**Example**:

```python
# core/<slice>/rest.py

from ninja import Router

router = Router()

...

# core/rest.py
from ninja import Router
from .<slice> import rest as <slice>

router = Router()
router.add_router("", <slice>.router)

```

## Resource definition

- Each resource is defined in the `rest.py` file or as a module within a `rest` package.
- The resource definition should come after the router declaration and before the endpoint definitions. It should have a header section to separate it from the router declaration and endpoint definitions.
- Each resource should subclass `Schema` from `ninja`.
- Related fields are usually prefetched in the service layer to optimize database queries. In the resource, they should be fetched directly, with a supression of `SynchronousOnlyOperation` to return None if it wasn't prefetched.
- Related fields that are lists should be defined as lists of the related resource schema.
- Try to avoid importing resources from other slices to prevent circular imports and deeply nested hierarchies. If necessary, define any related resources as minimal schemas within the current slice's rest module/package.
- Use UUIDs for referencing related resources instead of embedding the full resource schema, unless the full resource is required for the response.
- Do not include the id field in resource schemas; use uuid instead.
- Use the description parameter in Field to provide documentation for fields which will show up in the openapi specification.
- When using the Field object to document fields, defaults for non-required fields can be set to `...` for type-checking compliance. Mutable types (lists and dictionaries) should use `Field(default_factory=list)` or `Field(...)`.
- Related properties and dynamic properties are added using a resolve_<field_name> method.
- Resource properties are based on the model fields, with the following guidelines:
  - Use Optional types (e.g., `str | None`) for fields that can be null.
  - Use lists (e.g., `list[Post]`) for related fields that are many-to-many or one-to-many relationships.
  - Use the appropriate primitive types (e.g., `str`, `int`, `bool`, `float`, etc.) for basic fields.
  - For datetime fields, use `datetime.datetime` type.
  - For decimal fields, use `decimal.Decimal` type.

**Example**:

```python
from ninja import Schema, Field
from django.core.exceptions import SynchronousOnlyOperation
from contextlib import suppress

# =================================
# Resources
# =================================


class User(Schema):
    uuid: str = Field(..., description="UUID of the user.")
    full_name: str = Field(..., description="Full name of the user.")
    email: str = Field(..., description="Email of the user.")
    posts: list["Post"] = Field(..., description="List of the user's posts.")

    def resolve_posts(self) -> list["Post"]:
        with suppress(SynchronousOnlyOperation):
            if self.posts:
                return self.posts.all()
        return []

class Post(Schema):
    uuid: str
    title: str
    content: str
```

## Action-Specific Guidelines

- Each action should call the appropriate service layer function to perform the business logic, with the appropriate parameters.
- All service layer functions include a parameter for the authenticated user, usually named `auth_user`.
- Each action should have its own header section to separate it from other actions. The action header should include the http method name and the resource path.

### Browse

- Should return a list of resources.
- Should use the `router.get` decorator.
- Should be at the root path of the resource, e.g., `users/`.
- Should accept a query parameter for filtering, sorting, and searching.
- Should have an additional decorator for pagination.
- For type-checking compliance, it should be annotated to return a queryset of the resource model.

**Example**:

```python
from ninja import Field, Schema, Router, Query, CursorPagination
from lib.rest import UUIDList

from . import models, services

router = Router()

# =================================
# GET users/
# =================================


class BrowseQuery(Schema):
    search: str | None = Field(None, description="Search users by name.")
    sort: str | None = Field(None, description="Order users by the provided field. Options are name.")
    uuids: UUIDList | None = Field(None, description="List of user UUIDs to filter by")

@router.get(
    path="users/",
    response=response(200, list[User]),
    url_name="browse-users",
    operation_id="browse-users",
    summary="Users | Browse",
    tags=["Admin", "User"],
)
@paginate(CursorPagination[models.User])
@log_error()
async def browse(request: HttpRequest, query: Query[BrowseQuery]) -> "QuerySet[models.User]":
    return services.browse(
        auth_user=request.user,
        search=query.search,
        sort=query.sort,
        uuids=query.uuids,
    )
```

### Read

- Should return a single resource.
- Should use the `router.get` decorator.
- Should be at the path of the resource with the resource identifier, e.g., `users/{user_uuid}/`.
- Should accept the resource uuid as a path parameter.
**Example**:

```python
# =================================
# GET users/{user_uuid}/
# =================================

@router.get(
    path="users/{user_uuid}/",
    response=response(200, User),
    url_name="read-user",
    operation_id="read-user",
    summary="User | Read",
    tags=["Admin", "User"],
)
@log_error()
async def read(request: HttpRequest, user_uuid: str) -> User:
    return await services.read(
        auth_user=request.user,
        user_uuid=user_uuid,
    )
```

### Add

- Should create a new resource and return the created resource.
- Should use the `router.post` decorator.
- Should be at the root path of the resource, e.g., `users/`.
- Should accept a request body with the resource data, which should match the inputs expected by the service layer function.
- Should return a tuple with the status code and the created resource model class for type-checking compliance.
- Body parameters:
  - Should be defined in a separate class that subclasses `BaseInput` from `lib.rest`.
  - Can include a property for validators which define validators from `.validators` module. This property should return a dictionary where the keys are the field names and the values are tuples of validation rules.

**Example**:

```python
from ninja import Field
from lib.rest import BaseInput
from lib.validation import ValidationRule
from . import validators

# =================================
# POST users/
# =================================


class AddUserBody(BaseInput):
    full_name: str = Field(..., description="Full name of the user.")
    email: str = Field(..., description="Email of the user.")

    @property
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]::
        return {
            "email": (
                validators.EmailShouldBeUnique(),
            ),
        }

@router.post(
    path="users/",
    response=response(201, User),
    url_name="add-user",
    operation_id="add-user",
    summary="User | Add",
    tags=["Admin", "User"],
)
@log_error()
async def add(request: HttpRequest, body: AddUserBody) -> tuple[int, models.User]:
    user = await services.add(
        auth_user=request.user,
        full_name=body.full_name,
        email=body.email,
    )
```

### Edit

- Should update an existing resource and return the updated resource.
- Should use the `router.patch` decorator.
- Should be at the path of the resource with the resource identifier, e.g., `users/{user_uuid}/`.
- Should accept the resource uuid as a path parameter.
- Should accept a request body with the resource data to be updated, which should match the inputs expected by the service layer function. All fields in the body should usually be optional.
- Also supports validation rules in the same way as the [`Add`](#add) action.
- Should return a tuple with the status code and the updated resource model class for type-checking compliance.

**Example**:

```python
from ninja import Field
from lib.rest import BaseInput
from lib.validation import ValidationRule
from . import validators

# =================================
# PATCH users/{user_uuid}/
# =================================


class EditUserBody(BaseInput):
    full_name: str | None = Field(None, description="Full name of the user.")
    email: str | None = Field(None, description="Email of the user.")

    @property
    def validators(self) -> dict[str, tuple[ValidationRule, ...]]::
        return {
            "email": (
                validators.EmailShouldBeUnique(exclude_current=True),
            ),
        }

@router.patch(
    path="users/{user_uuid}/",
    response=response(200, User),
    url_name="edit-user",
    operation_id="edit-user",
    summary="User | Edit",
    tags=["Admin", "User"],
)
@log_error()
async def edit(request: HttpRequest, user_uuid: str, body: EditUserBody) -> tuple[int, models.User]:
    user = await services.edit(
        auth_user=request.user,
        user_uuid=user_uuid,
        full_name=body.full_name,
        email=body.email,
    )
    return 200, user
```

### Delete

- Should delete an existing resource.
- Should use the `router.delete` decorator.
- Should be at the path of the resource with the resource identifier, e.g., `users/{user_uuid}/`.
- Should accept the resource uuid as a path parameter.
- Should return a tuple with the status code and no content for type-checking compliance.

**Example**:

```python
# =================================
# DELETE users/{user_uuid}/
# =================================

@router.delete(
    path="users/{user_uuid}/",
    response=response(204),
    url_name="delete-user",
    operation_id="delete-user",
    summary="User | Delete",
    tags=["Admin", "User"],
)
@log_error()
async def delete(request: HttpRequest, user_uuid: str) -> tuple[int, None]:
    await services.delete(
        auth_user=request.user,
        user_uuid=user_uuid,
    )
    return 204, None
```

## Registering the router

- Each slice's rest module/package should be imported and registered in the main router located at `core/rest.py`.

**Example**:

```python
# core/rest.py
# <slice> is the name of the slice being registered
from ninja import Router
from .<slice> import rest as <slice>

router = Router()
router.add_router("", <slice>.router)
```
