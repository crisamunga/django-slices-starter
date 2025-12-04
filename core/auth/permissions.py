from lib.permissions import permission

from .models import AnonymousUser, User


@permission
async def can_get_profile(*, auth_user: User | AnonymousUser) -> bool:
    return auth_user.is_active
