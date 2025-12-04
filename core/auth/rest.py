from uuid import UUID

from django.http import HttpRequest
from ninja import Field, Router

from lib.logs.decorators import log_error
from lib.rest import BaseObjectResource, response

from . import models, services

router = Router()

# =================================
# Resources
# =================================


class ProfileResource(BaseObjectResource):
    uuid: UUID = Field(..., description="UUID of the user.")
    full_name: str = Field(..., description="Full name of the user.")
    email: str = Field(..., description="Email of the user.")


# =================================
# GET profile/
# =================================


@router.get(
    path="profile/",
    response=response(200, ProfileResource),
    url_name="profile-read",
    operation_id="profile-read",
    summary="Profile | Read",
    tags=["User"],
)
@log_error()
async def get_profile(request: HttpRequest) -> models.User | None:
    """Endpoint to retrieve the currently logged-in user's profile."""
    return await services.get_profile(auth_user=request.user)
