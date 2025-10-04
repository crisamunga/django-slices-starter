from factory.django import DjangoModelFactory

from ..models import Role


class RoleFactory(DjangoModelFactory[Role]):
    class Meta:
        model = Role
        skip_postgeneration_save = True
