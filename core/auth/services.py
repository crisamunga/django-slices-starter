from . import permissions
from .models import AnonymousUser, User


async def get_profile(*, auth_user: User | AnonymousUser) -> User | None:
    await permissions.can_get_profile(auth_user=auth_user)
    if auth_user.is_active:
        await auth_user.aprefetch_related("emailaddress_set")
        return auth_user
    return None
