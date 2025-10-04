from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from core.models import Role
from lib.models import BaseModel

# Create your models here.


class UserManager(BaseUserManager["User"]):
    async def _create_user(
        self,
        email: str,
        identity_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool = True,
    ) -> "User":
        """
        Create and save a user with the given email and identity_id.
        """
        if not email:
            raise ValueError("The user's email must be set")
        if not identity_id:
            raise ValueError("The user's identity_id must be set")
        email = self.normalize_email(email)
        user = User(
            identity_id=identity_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )
        user.set_unusable_password()
        await user.asave(using=self._db)
        return user

    async def create_user(
        self,
        email: str,
        identity_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool = True,
        **kwargs: str,
    ) -> "User":
        return await self._create_user(
            email=email,
            identity_id=identity_id,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )

    async def create_superuser(
        self,
        email: str,
        identity_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool = True,
        **kwargs: str,
    ) -> "User":
        # TODO: Add superuser permissions
        return await self._create_user(
            email=email,
            identity_id=identity_id,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )


class User(BaseModel, AbstractBaseUser):
    """
    User model.
    """

    email = models.EmailField(unique=True, db_comment="THe user's email address")
    first_name = models.CharField(max_length=255, blank=True, db_comment="The user's first name")
    last_name = models.CharField(max_length=255, blank=True, db_comment="The user's last name")
    is_active = models.BooleanField(default=True, db_comment="Whether this user should be treated as active")
    roles = models.ManyToManyField(to="core.Role", related_name="users")

    REQUIRED_FIELDS = ("email",)

    # allauth settings
    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    ACCOUNT_SIGNUP_FIELDS = ("email*", "password1*", "password2*")
    ACCOUNT_LOGIN_METHODS = ("email",)

    objects: UserManager = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)

    async def has_all_roles(self, *roles: str | Role) -> bool:
        roles_to_check: list[str] = []
        for role in roles:
            if isinstance(role, str):
                roles_to_check += [role]
            else:
                roles_to_check += [role.name]
        roles_to_check = list(set(roles_to_check))
        return await self.roles.filter(name__in=roles_to_check).acount() == len(roles_to_check)

    async def has_any_role(self, *roles: str | Role) -> bool:
        roles_to_check: list[str] = []
        for role in roles:
            if isinstance(role, str):
                roles_to_check += [role]
            else:
                roles_to_check += [role.name]
        return await self.roles.filter(name__in=roles_to_check).aexists()

    async def add_roles(self, *roles: str | Role) -> None:
        roles_to_add: list[Role] = []
        for role in roles:
            if isinstance(role, str):
                roles_to_add += [await Role.objects.aget(name=role)]
            else:
                roles_to_add += [role]

        await self.roles.aadd(*roles_to_add)

    async def set_roles(self, *roles: str | Role) -> None:
        roles_to_set: list[Role] = []
        for role in roles:
            if isinstance(role, str):
                roles_to_set += [await Role.objects.aget(name=role)]
            else:
                roles_to_set += [role]

        await self.roles.aset(roles_to_set)

    async def remove_roles(self, *roles: str | Role) -> None:
        roles_to_remove: list[Role] = []
        for role in roles:
            if isinstance(role, str):
                roles_to_remove += [await Role.objects.aget(name=role)]
            else:
                roles_to_remove += [role]

        await self.roles.aremove(*roles_to_remove)

    async def is_admin_or_system(self) -> bool:
        return await self.has_any_role(Role.Names.admin, Role.Names.system)


__all__ = ["User"]
