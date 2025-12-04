import uuid
from typing import TYPE_CHECKING, Self

from asgiref.sync import sync_to_async
from django.db import models
from django.db.models.query import aprefetch_related_objects, prefetch_related_objects

if TYPE_CHECKING:
    from core.models import User


class BaseModel(models.Model):
    """
    Base model for all models.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        db_comment="UUID of the model. Meant for access.",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_comment="When the model was created.")
    updated_at = models.DateTimeField(auto_now=True, db_comment="When the model was last updated.")
    created_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created",
        db_comment="The user who created the model.",
        db_index=True,
    )
    updated_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_updated",
        db_comment="The user who last updated the model.",
        db_index=True,
    )

    class Meta:
        abstract = True

    async def aprefetch_related(self, *related: str) -> Self:
        """
        Fetch related objects.
        """
        await aprefetch_related_objects([self], *related)
        return self

    def prefetch_related(self, *related: str) -> Self:
        """
        Fetch related objects.
        """
        prefetch_related_objects([self], *related)
        return self

    async def with_audired(self) -> Self:
        """
        Fetch the user who created and updated the model.
        """
        await self.aprefetch_related("created_by", "updated_by")
        return self

    @sync_to_async
    def acreated_by(self) -> "User | None":
        """
        Get the user who created the model.
        """
        return self.created_by

    @sync_to_async
    def aupdated_by(self) -> "User | None":
        """
        Get the user who created the model.
        """
        return self.updated_by


class BaseLookUpManagerMixin[T: BaseLookUp]:
    """
    Look up table manager.
    """

    async def get_by_name(self, name: str) -> T:
        """
        Get a record by name.
        """
        return await self.aget(name=name)  # type: ignore


class BaseLookUpManager(BaseLookUpManagerMixin["BaseLookUp"], models.Manager["BaseLookUp"]): ...


class BaseLookUp(BaseModel):
    """
    Look up table model.
    """

    objects: models.Manager["BaseLookUp"] | BaseLookUpManager = BaseLookUpManager()

    name = models.CharField(max_length=255, unique=True, db_comment="The name of the record in the look up table.")
    display_name = models.CharField(
        max_length=255, blank=True, db_comment="The display name of the record in the look up table."
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name if not self.display_name else f"{self.name} ({self.display_name})"
