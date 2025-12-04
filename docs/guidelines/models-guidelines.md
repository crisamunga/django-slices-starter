---
applyTo: '**/models.py, **/models/*.py'
---

Apply the [python coding guidelines](./python.instructions.md) to all code.

# Models Instructions

- Place Django models in a `models.py` file within the relevant slice or module.
- Always explicitly define the `Meta` class within each model and always include these attributes:
  - `db_table`: Snake case table name. Doesn't include app name prefix. e.g. `user`. Use singular form.
  - `verbose_name`: Human readable singular name for the model.
  - `verbose_name_plural`: Human readable plural name for the model.
  - `default_permissions`: Set to an empty tuple `()` to disable default Django permissions.
  - `ordering`: Define a default ordering for querysets, typically by `-created_at`.
- Always define a `__str__` method for each model that returns a human readable representation of the model instance.
- use string representations for foreign key and many to many relationships to avoid circular imports.
- If other models need to be imported (e.g. for custom model, manager or queryset methods), import them within methods instead of at the module level to avoid circular imports.
- If models from other slices are only needed for type annotations, use forward references (i.e. strings) and import them in the if TYPE_CHECKING block to avoid circular imports.
- Always define models with the fields at the top of the class, followed by any custom managers or querysets, followed by custom class level properties, then the Meta class, and finally any methods, starting with internal dunder methods like `__str__`.

## Lookup Models

- Prefer to use lookup models for reference data instead of choice fields.
- Lookup models extend `lib.models.LookupModel` for common lookup table functionality.
- Managers for lookup models extend `lib.models.BaseLookUpManagerMixin`.

**Example:**

```python
from django.db import models

from lib.models import BaseLookUp, BaseLookUpManagerMixin


class GenreManager(BaseLookUpManagerMixin["Genre"], models.Manager["Genre"]): ...


class Genre(BaseLookUp):
    objects: GenreManager = GenreManager()

    class Meta:
        db_table = "genre"
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        default_permissions = ()
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Genre: {self.name}"


__all__ = ["Genre"]
```

## General models

- Each model is defined as a class extending `lib.models.BaseModel` which includes common fields and methods.
- You can define custom managers by extending `django.db.models.Manager` or by creating a custom queryset by extending `django.db.models.QuerySet`.
- Do not annotate model fields ; let mypy do the inference itself.
- Always define `__all__` at the end of the module to explicitly declare public API of the module.
- Always create explicit models for many to many relationships instead of using Django's implicit through tables. This allows for easier extension in the future if additional fields are needed on the relationship.

**Example:**

```python

from django.db import models
from django.utils import timezone

from lib.asyncutils import alist
from lib.models import BaseModel


class PostQuerySet(models.QuerySet["Post"]):
    def published(self) -> "PostQuerySet":
        return self.filter(published_at__isnull=False, published_at__lte=timezone.now().date())

class Post(BaseModel):
    title = models.CharField(max_length=255)
    summary = models.TextField(null=True)
    author = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="posts")
    genres = models.ManyToManyField("core.Genre", related_name="posts", through="core.PostGenre", through_fields=("post", "genre"))
    published_at = models.DateField(null=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        db_table = "post"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        default_permissions = ()

    def __str__(self) -> str:
        return f"Post: {self.title}"

class PostGenre(BaseModel):
    post = models.ForeignKey("core.Post", on_delete=models.CASCADE, related_name="post_genres")
    genre = models.ForeignKey("core.Genre", on_delete=models.CASCADE, related_name="post_genres")

    class Meta:
        db_table = "post_genre"
        verbose_name = "Post Genre"
        verbose_name_plural = "Post Genres"
        default_permissions = ()


    def __str__(self) -> str:
        return f"PostGenre: Post {self.post_id} - Genre {self.genre_id}"
```

## Registering Models

- All models are registered by importing them in the apps's `models.py` file to ensure they are discovered by Django.

**Example:**

```python
# core/models.py
# <slice> is the name of the slice being registered
from .<slice>.models import *
```
