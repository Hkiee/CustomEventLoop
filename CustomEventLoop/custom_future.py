from typing import (Any,
                    Callable,
                    Generator)


class CustomFuture:
    def __init__(self) -> None:
        self._result: Any = None
        self._is_finished: bool = False
        self._done_callback: Callable[[Any], None] | None = None

    def result(self) -> Any:
        return self._result

    def is_finished(self) -> bool:
        return self._is_finished

    def set_result(self, result: Any) -> None:
        self._result = result
        self._is_finished = True
        if self._done_callback:
            self._done_callback(result)

    def add_done_callback(self, fn: Callable[[Any], None]) -> None:
        self._done_callback = fn

    def __await__(self) -> Generator:
        if not self._is_finished:
            yield self
        return self.result()
