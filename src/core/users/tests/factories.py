from factory.django import DjangoModelFactory

from ..models import User


class UserFactory(DjangoModelFactory[User]):
    class Meta:
        model = User
        skip_postgeneration_save = True
