from collections.abc import Generator
from typing import Any

from strawberry import extensions

from lib.errors import UnauthenticatedError


class AuthenticationExtension(extensions.SchemaExtension):
    def on_operation(self) -> Generator[None, Any]:
        context = self.execution_context
        if not context.context.request.user.is_authenticated:
            raise UnauthenticatedError
        yield
