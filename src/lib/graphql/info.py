from typing import Any, TypeVar

import strawberry
from strawberry.types.nodes import InlineFragment, Selection

from core.models import User

from .context import Context
from .loaders import DataLoader

T = TypeVar("T", default=Any)


class Info(strawberry.Info[Context, T]):
    @property
    def user(self) -> User:
        return self.context.request.user

    def get_selection(self, *, path: list[str], depth: int = 1) -> set[str]:  # noqa: C901 - Necessary complexity
        """
        Get the selected fields in the query by recursing down the selection set.
        """
        if depth == 0:
            return set()

        def _get_selections(field: Selection, path: list[str], parent: str | None, depth: int = 1) -> set[str]:
            if depth == 0:
                return set()
            if not path:
                selections: list[str] = []
                for subfield in field.selections:
                    if isinstance(subfield, InlineFragment):
                        selections.extend(_get_selections(subfield, path, parent, depth))
                    else:
                        field_name = f"{parent}.{subfield.name}" if parent else subfield.name
                        selections.append(field_name)

                        if depth > 1:
                            selections.extend(_get_selections(subfield, path, field_name, depth - 1))
                return set(selections)

            for subfield in field.selections:
                if isinstance(subfield, InlineFragment):  # TODO: handle inline fragments
                    continue
                if subfield.name == path[0]:
                    return _get_selections(subfield, path[1:], None, depth)

            return set()

        for field in self.selected_fields:
            if isinstance(field, InlineFragment):  # TODO: handle inline fragments
                continue
            if field.name == path[0]:
                return _get_selections(field, path[1:], None, depth)

        return set()

    def get_includes(self, *, path: list[str], depth: int = 1, selection_include_mapping: dict[str, str]) -> list[str]:
        selections = self.get_selection(path=path, depth=depth)
        includes: list[str] = []
        for selection, include in selection_include_mapping.items():
            if selection in selections:
                includes.append(include)
        return includes

    def get_loader[T: DataLoader[Any, Any]](self, type_: type[T]) -> T:
        if getattr(self, "_loaders", None) is None:
            self._loaders: dict[str, DataLoader[Any, Any]] = {}
        if type_.__name__ not in self._loaders:
            self._loaders[type_.__name__] = type_()
        return self._loaders[type_.__name__]  # type: ignore # Return the loader instance
