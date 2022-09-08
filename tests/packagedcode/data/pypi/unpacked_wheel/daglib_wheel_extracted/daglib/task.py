from __future__ import annotations as _annotations  # avoids name conflict with constructor arg

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Arg:
    """Mutable argument dataclass. Used as an abstraction of a function argument
    with a name, type, and default value."""

    name: str
    type: type | None = field(default=None)
    default: Any | None = field(default=None)


class Task:
    """Mutable task object with chained setters"""

    def __init__(
        self,
        fn: Callable[..., Any],
        *,
        name: str,
        description: str | None = "",
        annotations: dict[str, type] | None = None,
        return_type: type | None = None,
        defaults: tuple[Any, ...] = (),
        args: list[Arg] | None = None,
    ) -> None:
        """

        :param fn: Arbitrary function (can include lambda and partial functions)
        :param name: Name of task
        :param description: Description of task
        :param annotations: Input and return value type annotations
        :param return_type: Return type
        :param defaults: Default values
        :param args: Arguments for task
        """
        self._fn = fn
        self._name = name
        self._description = description
        self._annotations = annotations if annotations else {}
        self._return_type = return_type
        self._defaults = defaults
        self._args = args if args else []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)

    @property
    def fn(self) -> Callable[..., Any]:
        return self._fn

    def set_fn(self, fn: Callable[..., Any]) -> Task:
        self._fn = fn
        return self

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> Task:
        self._name = name
        return self

    @property
    def description(self) -> str | None:
        return self._description

    def set_description(self, description: str) -> Task:
        self._description = description
        return self

    @property
    def annotations(self) -> dict[str, type]:
        return self._annotations

    def set_annotations(self, annotations: dict[str, type]) -> Task:
        self._annotations = annotations
        return self

    @property
    def return_type(self) -> type | None:
        return self._return_type

    def set_return_type(self, return_type: type | None) -> Task:
        self._return_type = return_type
        return self

    @property
    def defaults(self) -> tuple[Any, ...]:
        return self._defaults

    def set_defaults(self, defaults: tuple[Any, ...]) -> Task:
        self._defaults = defaults
        return self

    @property
    def args(self) -> list[Arg]:
        return self._args

    def set_args(self, args: list[Arg]) -> Task:
        self._args = args
        return self

    # noinspection PyUnresolvedReferences
    @classmethod
    def from_function(cls, fn: Callable[..., Any], name: str | None = None, args: list[Arg] | None = None) -> Task:
        """
        Create Task object from function. Values from function metadata will be passed to the Task
        constructor.

        :param fn: Arbitrary function (can include lambda and partial functions)
        :param name: Optional name. If not provided then name will be grabbed from function metadata
        :param args: Optional list of custom arguments. If not provided then args will be grabbed from function metadata
        :return: Task object
        """
        name = fn.__name__ if not name else name
        description = fn.__doc__
        annotations = fn.__annotations__
        return_type = annotations.get("return")
        defaults = tuple(reversed(fn.__defaults__)) if fn.__defaults__ else tuple()  # type: ignore
        if not args:
            args = [Arg(n, None, None) for n in fn.__code__.co_varnames[: fn.__code__.co_argcount]]
            for arg in args:
                arg.type = annotations.get(arg.name)
            for i, d in enumerate(defaults):
                args[len(args) - 1 - i].default = d

        return Task(
            fn,
            name=name,
            description=description,
            annotations=annotations,
            return_type=return_type,
            defaults=defaults,
            args=args,
        )

    @classmethod
    def from_object(cls, obj: Any, name: str) -> Task:
        fn: Callable[[], Any] = lambda: obj
        return Task.from_function(fn, name)
