import logging
from typing import TYPE_CHECKING, Any

from allauth.account.signals import user_logged_in, user_signed_up
from django.dispatch import receiver

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .models import User

logger = logging.getLogger(__name__)


@receiver(user_signed_up)
async def handle_user_signed_up(sender: Any, request: "HttpRequest", user: "User", **kwargs: Any) -> None:  # noqa: ARG001 # Arguments are required by signal
    """
    Signal receiver to perform actions upon user signup.
    """
    logger.info("New user signed up", extra={"user_id": user.uuid})


@receiver(user_logged_in)
async def handle_user_logged_in(sender: Any, request: "HttpRequest", user: "User", **kwargs: Any) -> None:  # noqa: ARG001 # Arguments are required by signal
    """
    Signal receiver to perform actions upon user login.
    """
    logger.info("User logged in", extra={"user_id": user.uuid})
