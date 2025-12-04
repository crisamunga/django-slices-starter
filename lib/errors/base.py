from django.utils.translation import gettext as _


class BaseError(Exception):
    code: str
    message: str
    metadata: dict[str, str | int | bool | list[str] | list[int] | list[bool] | list[str | int] | None]

    def __init__(
        self,
        description: str,
        code: str = "internal_error",
        message: str | None = None,
        **kwargs: str | int | bool | list[str] | list[str | int] | list[int] | list[bool] | None,
    ) -> None:
        """Base error class that defines how we structure our errors.

        Args:
            description (str): Descriptive message of what failed
            code (str): Error code to identify the type of error. Defaults to `internal_error`
            message (str | None): Message to show to the user on what failed.
                Defaults to `An unexpected error occurred.`
        """
        self.code = code
        self.message = message or _("An unexpected error occurred.")
        self.metadata = kwargs
        super().__init__(f"{self.__class__.__name__}: {description}")


class UserError(BaseError):
    """Error class for errors that can be resolved by the user."""


class UnauthenticatedError(BaseError):
    def __init__(self, code: str = "unauthenticated", message: str | None = None) -> None:
        super().__init__(
            "User not signed in",
            message=message or _("You must sign in to perform this action."),
            code=code,
        )


class AuthorizationError(BaseError):
    def __init__(
        self,
        description: str,
        *,
        code: str = "forbidden",
        message: str | None = None,
        permission_required: str | None = None,
    ) -> None:
        super().__init__(
            description,
            code=code,
            message=message or _("You don't have permission to perform this action."),
            permission_required=permission_required,
        )


class NotFoundError(BaseError):
    def __init__(
        self,
        description: str,
        *,
        code: str = "not_found",
        message: str | None = None,
        missing_resource: str | None = None,
    ) -> None:
        super().__init__(
            description,
            code=code,
            message=message or _("The requested resource was not found."),
            missing_resource=missing_resource,
        )


class InputError(BaseError):
    path: list[str | int]

    def __init__(
        self,
        description: str,
        *,
        code: str = "invalid_input",
        message: str | None = None,
        path: list[str | int],
    ) -> None:
        self.path = path
        super().__init__(
            description,
            code=code,
            message=message or _("Invalid input."),
            field=path,
        )
