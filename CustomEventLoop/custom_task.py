from typing import Coroutine, Any

from custom_future import CustomFuture


class CustomTask(CustomFuture):
    def __init__(self, coro: Coroutine, loop) -> None:
        super().__init__()
        self._coro: Coroutine = coro
        self._loop = loop
        self._task_state: Any | None = None
        self._current_result: Any | None = None
        loop.register_task(self)

    def step(self) -> None:
        try:
            if self._task_state is None:
                self._task_state = self._coro.send(None)

            if isinstance(self._task_state, CustomFuture):
                self._task_state.add_done_callback(self._future_done)

        except StopIteration as si:
            self.set_result(si.value)

    def _future_done(self, result: Any | None) -> None:
        self._current_result = result

        try:
            self._task_state = self._coro.send(self._current_result)

        except StopIteration as si:
            self.set_result(si.value)
