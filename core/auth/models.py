from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import functions

from lib.models import BaseModel

# Create your models here.


class UserManager(BaseUserManager["User"]):
    async def _create_user(
        self,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool = True,
        password: str | None = None,
    ) -> "User":
        """
        Create and save a user with the given email and identity_id.
        """
        if not email:
            raise ValueError("The user's email must be set")
        email = self.normalize_email(email)
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        await user.asave(using=self._db)
        return user

    async def create_user(
        self,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool = True,
        password: str | None = None,
        **kwargs: str,
    ) -> "User":
        return await self._create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            password=password,
        )


class User(BaseModel, AbstractBaseUser):
    """
    User model.
    """

    email = models.EmailField(unique=True, db_comment="THe user's email address")
    first_name = models.CharField(max_length=255, blank=True, db_comment="The user's first name")
    last_name = models.CharField(max_length=255, blank=True, db_comment="The user's last name")
    is_active = models.BooleanField(default=True, db_comment="Whether this user should be treated as active")
    full_name = models.GeneratedField(
        output_field=models.TextField(),
        expression=functions.Trim(
            functions.Concat("first_name", models.Value(" "), "last_name"), output_field=models.TextField()
        ),
        db_persist=True,
        db_comment="The user's full name",
    )

    objects: UserManager = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)


__all__ = ["AnonymousUser", "User"]
