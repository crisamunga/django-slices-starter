---
agent: 'agent'
model: GPT-4o
tools: ['search/codebase']
description: 'Generate a slice in the core app'
---

Get the name of the new slice to be created in the core app. Each slice typically represents a resource or a feature in the application.
Create a new slice in the core app following the established conventions. The slice should have this folder structure:

```
core/<slice-name>/
  ├── tests/
  │   ├── __init__.py
  │   ├── factories.py
  │   ├── test_graphql.py
  │   ├── test_rest.py
  │   ├── test_services.py
  │   └── test_validators.py
  ├── __init__.py
  ├── errors.py
  ├── graphql.py
  ├── models.py
  ├── permissions.py
  ├── rest.py
  ├── services.py
  └── validators.py
```

Once you have created these files, add the following boilerplate code to these files:

`rest.py`:
```python
from django.http import HttpRequest
from ninja import Field, Router, Schema

from lib.logs.decorators import log_error
from lib.rest import response

from . import models, services

router = Router()


# =================================
# Resources
# =================================


# =================================
# GET <plural-slice-name>/
# =================================


# =================================
# POST <plural-slice-name>/
# =================================


# =================================
# GET <plural-slice-name>/<single-slice-name>_uuid/
# =================================


# =================================
# PATCH <plural-slice-name>/><single-slice-name>_uuid/
# =================================

# =================================
# DELETE <plural-slice-name>/<single-slice-name>_uuid/
# =================================

```

`services.py`:
```python
from uuid import UUID

from core.models import User
from lib.errors import not_found_on_error

from . import models, permissions

# Add service functions here

```

`models.py`:
```python
from django.db import models
from lib.models import BaseModel, BaseLookUp, BaseLookUpManagerMixin

class <slice-name-in-camel-case>(BaseModel):
    # Define fields here

    class Meta:
        db_table = "<singular-slice-name>"
        verbose_name = "<slice name in title case>"
        verbose_name_plural = "<plural slice name in title case>"
        ordering = ("-created_at",)
```

`permissions.py`:
```python
from core.models import User
from core.auth.authorizer import authorizer

# Define permission functions here
```

`validators.py`:
```python
from lib.validation import ValidationRule

# Define validation functions here
```

`errors.py`:
```python
from lib.errors import BaseError

# Define custom error classes here
```

`graphql.py`:
```python
from typing import Annotated, Any
from uuid import UUID
import contextlib

import strawberry

import core.models
from lib.graphql import Base, DataLoader, Info, make_schema, mutations, relay
from lib.logs import log_error

from . import services

# ------------------------------------------------------------------------------
# Data loader
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Types
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Queries
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Mutations
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------------------

```
