from __future__ import annotations

import uuid
from typing import Any, Callable

import networkx as nx
from dask.delayed import Delayed
from dask.optimization import cull

from daglib.task import Task, Arg


class Dag:
    def __init__(self, name: str = uuid.uuid4().hex, description: str = "") -> None:
        self.name = "".join(x for x in name if x.isalnum()).lower()
        self.description = description
        self._tasks_by_name: dict[str, Task] = {}
        self.nxg = nx.DiGraph()

    @property
    def run_id(self) -> str:
        return f"run_{uuid.uuid1().hex}"

    def add_subdag(self, other: Dag) -> None:
        self._tasks_by_name |= other._tasks_by_name

    def register_task(self, task: Task) -> Task:
        self._tasks_by_name[task.name] = task
        return task

    def register_task_from_function(
        self, fn: Callable[..., Any], name: str | None = None, args: list[Arg] | None = None
    ) -> Callable[..., Any]:
        task = Task.from_function(fn, name=name, args=args)
        self.register_task(task)
        return fn

    def task(self) -> Any:
        def register(fn: Callable[..., Any]) -> Callable[..., Any]:
            return self.register_task_from_function(fn)

        return register

    def _build_graph(self) -> None:
        edges = [(self._tasks_by_name[arg.name], task) for task in self._tasks_by_name.values() for arg in task.args]
        self.nxg = nx.DiGraph(edges)

    @property
    def _dsk(self) -> dict[str, tuple[Any, ...]]:
        return {task.name: tuple([task.fn, *[arg.name for arg in task.args]]) for task in nx.topological_sort(self.nxg)}

    @property
    def _keys(self) -> list[str]:
        return [task.name for task in self.nxg.nodes if not list(self.nxg.successors(task))]

    def materialize(self, to_step: str | Callable[..., Any] | None = None, optimize: bool = False) -> Delayed:
        self._build_graph()
        keys: list[str] | str = self._keys
        if len(keys) == 1:
            keys = keys[0]
        dsk = self._dsk
        if to_step:
            if callable(to_step):
                keys = to_step.__name__
            optimize = True
        if optimize:
            layers, _ = cull(dsk, keys)
        return Delayed(keys, dsk)

    def run(self, to_step: str | Callable[..., Any] | None = None, optimize: bool = False) -> Any:
        return self.materialize(to_step, optimize).compute()

    # noinspection PyShadowingBuiltins
    def visualize(
        self,
        to_step: str | Callable[..., Any] | None = None,
        optimize: bool = False,
        filename: str | None = None,
        format: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self.materialize(to_step, optimize).visualize(filename, format, **kwargs)
