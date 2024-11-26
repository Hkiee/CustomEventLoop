import selectors
import socket
import functools

from typing import List, Coroutine, Any, Callable

from custom_task import CustomTask
from custom_future import CustomFuture


class CustomEventLoop:
    _tasks_to_run: List[CustomTask] = []

    def __init__(self) -> None:
        self.selectors: selectors.DefaultSelector = selectors.DefaultSelector()
        self.current_result: Any | None = None

    def _register_socket_to_read(self, sock: socket.socket, callback: Callable) -> CustomFuture:
        future = CustomFuture()

        try:
            self.selectors.get_key(sock)
        except KeyError:
            sock.setblocking(False)
            self.selectors.register(sock, selectors.EVENT_READ,
                                    functools.partial(callback, future))

        else:
            self.selectors.modify(sock, selectors.EVENT_READ,
                                  functools.partial(callback, future))

        return future

    def sock_close(self, sock: socket.socket) -> None:
        self.selectors.unregister(sock)
        sock.close()

    def register_task(self, task: CustomTask) -> None:
        self._tasks_to_run.append(task)

    def _set_current_result(self, result: Any) -> None:
        self.current_result = result

    async def sock_recv(self, sock: socket.socket) -> CustomFuture:
        print(f'Registering socket to listen for data')
        return await self._register_socket_to_read(sock, self.recieved_data)

    async def sock_accept(self, sock: socket.socket) -> CustomFuture:
        print('Registering socket to accept connections...')
        return await self._register_socket_to_read(sock, self.accept_connection)

    def recieved_data(self, future: CustomFuture,
                      sock: socket.socket) -> None:
        data = sock.recv(4096)
        future.set_result(data)

    def accept_connection(self, future: CustomFuture,
                          sock: socket.socket) -> None:
        conn = sock.accept()
        future.set_result(conn)

    def run(self, coro: Coroutine) -> None:
        self.current_result = coro.send(None)

        while True:
            try:
                if isinstance(self.current_result, CustomFuture):
                    self.current_result.add_done_callback(self._set_current_result)
                    if self.current_result.result() is not None:
                        self.current_result = coro.send(self.current_result.result())
                else:
                    self.current_result = coro.send(self.current_result)
            except StopIteration as si:
                return si.value

            for task in self._tasks_to_run:
                task.step()

            self._tasks_to_run = [task for task in self._tasks_to_run if not task.is_finished()]

            events = self.selectors.select()
            print('Selector has an event, processing...')
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
