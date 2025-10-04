from django.db import models

from lib.models import BaseLookUp, BaseLookUpManagerMixin, BaseModel


class RoleManager(BaseLookUpManagerMixin["Role"], models.Manager["Role"]):
    async def get_admin(self) -> "Role":
        role, _ = await self.aget_or_create(name=Role.Names.admin, display_name=Role.Names.admin.title())
        return role

    async def get_user(self) -> "Role":
        role, _ = await self.aget_or_create(name=Role.Names.user, display_name=Role.Names.user.title())
        return role

    async def get_system(self) -> "Role":
        role, _ = await self.aget_or_create(name=Role.Names.system, display_name=Role.Names.system.title())
        return role


class Role(BaseLookUp, BaseModel):
    """
    Role model.
    """

    domain = models.CharField(max_length=255, db_comment="The role's domain")
    description = models.TextField(blank=True, db_comment="The role's description")

    objects: RoleManager = RoleManager()

    class Meta:
        db_table = "role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ("-created_at",)

    class Names:
        admin = "admin"
        user = "user"
        system = "system"

    def __str__(self) -> str:
        return f"{self.domain} | {super().__str__()}"


__all__ = ["Role"]
