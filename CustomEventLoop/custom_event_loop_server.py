import socket

from custom_event_loop import CustomEventLoop
from custom_task import CustomTask


async def reading_data_from_client(client_socket: socket.socket,
                                   loop: CustomEventLoop) -> None:
    print(f'Trying to get some data from client\n'
          f'Client_socket info: {client_socket}')
    try:
        while data := await loop.sock_recv(client_socket):
            print(f'We got data from: {client_socket}\n'
                  f'data: {data}')
    finally:
        loop.sock_close(client_socket)



async def connection_listener(server_socket: socket.socket,
                              loop: CustomEventLoop) -> None:
    while True:
        print(f'Waiting for connection to: {server_socket}')
        client_socket, addr = await loop.sock_accept(server_socket)
        print(f'We got connection from: {addr}'
              f'Detail info: {client_socket}')
        CustomTask(reading_data_from_client(client_socket, loop), loop)


async def main(loop: CustomEventLoop) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind(('localhost', 5000))
    server_socket.listen()

    await connection_listener(server_socket, loop)


if __name__ == '__main__':
    loop = CustomEventLoop()
    loop.run(main(loop))