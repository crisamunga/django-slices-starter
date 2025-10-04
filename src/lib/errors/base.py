from django.utils.translation import gettext_lazy as _

from lib import messages


class BaseError(Exception):
    message: messages.Message
    metadata: dict[str, str | int | bool | list[str] | list[int] | list[bool] | list[str | int] | None]

    def __init__(
        self,
        description: str,
        message: messages.Message | None = None,
        **kwargs: str | int | bool | list[str] | list[str | int] | list[int] | list[bool] | None,
    ) -> None:
        """Base error class that defines how we structure our errors.

        Args:
            description (str): Descriptive message of what failed
            message (messages.Message | None): Message to show to the user on what failed.
                Defaults to `unexpected_error`
        """
        self.message = message or messages.get_message(
            code="unexpected_error", message=_("An unexpected error occurred.")
        )
        self.metadata = kwargs
        super().__init__(f"{self.__class__.__name__}: {description}")


class UserError(BaseError):
    """Error class for errors that can be resolved by the user."""


class UnauthenticatedError(BaseError):
    def __init__(self, message: messages.Message | None = None) -> None:
        super().__init__(
            "User not signed in",
            message=message
            or messages.get_message(code="unauthenticated", message=_("You must sign in to perform this action.")),
        )


class AuthorizationError(BaseError):
    def __init__(
        self,
        description: str,
        permission_required: str | None = None,
    ) -> None:
        super().__init__(
            description,
            message=messages.get_message(
                code="unauthorized", message=_("You don't have permission to perform this action.")
            ),
            permission_required=permission_required,
        )


class NotFoundError(BaseError):
    def __init__(self, description: str, missing_resource: str | None = None) -> None:
        super().__init__(
            description,
            message=messages.get_message(code="not_found", message=_("The requested resource was not found.")),
            missing_resource=missing_resource,
        )


class InputError(BaseError):
    path: list[str | int]

    def __init__(
        self,
        description: str,
        *,
        message: messages.Message | None = None,
        path: list[str | int],
    ) -> None:
        self.path = path
        super().__init__(
            description,
            message=message or messages.get_message(code="invalid_input", message=_("Invalid input.")),
            field=path,
        )


class InputErrorGroup(ExceptionGroup):
    exceptions: tuple[InputError, ...]
