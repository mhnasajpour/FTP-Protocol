from socket import *
from random import randint
import os


def get_folder_size(folder_path):
    size = 0
    for path, dirs, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size


class FTP_Server:
    def __init__(self):
        self.location = __file__[:-9] + 'sources'
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('127.0.0.1', 2121))
        self.server.listen(10)
        while True:
            self.start_server()

    def start_server(self):
        connection, address = self.server.accept()
        print(f'The client with address {address} was connected.')
        connection.send(self.location.encode())
        while True:
            request = connection.recv(16384).decode()
            if request == '!close':
                connection.close()
                break
            response = self.define_command(request)
            connection.send(response.encode())
            if request.startswith('dwld') and int(response):
                self.send_file(request[5:], int(response))

    def define_command(self, request):
        if request[0] == '\\':
            return self.list(request)
        elif request[0] == '.':
            return self.is_valid_path(request[1:])
        elif request.startswith('dwld'):
            return self.getPort_to_dwld(request[5:])

    def list(self, request):
        total_size = 0
        response = '\n'
        path = self.location + request

        for index in os.listdir(path):
            abspath = os.path.join(path, index)
            if os.path.isdir(abspath):
                total_size += get_folder_size(abspath)
                response += f'> {index}   {get_folder_size(abspath)}\n'
            else:
                total_size += os.path.getsize(abspath)
                response += f'  {index}   {os.path.getsize(abspath)}\n'

        response += '-'*25
        response += f'\n Total_size: {total_size}\n'

        return response

    def is_valid_path(self, request):
        path = f'{self.location}{request}'
        if os.path.abspath(path).startswith(self.location):
            return str(os.path.exists(path))
        return 'False'

    def getPort_to_dwld(self, request):
        if self.is_valid_path(request) == 'True':
            return str(randint(3000, 50000))
        return '0'

    def send_file(self, path, port_number):
        dwld_socket = socket(AF_INET, SOCK_STREAM)
        dwld_socket.bind(('127.0.0.1', port_number))
        dwld_socket.listen(1)
        dwld_connection, addr = dwld_socket.accept()
        print(
            f'User with adrress {addr} downloaded file from path "{path[1:]}"')
        path = f'{self.location}{path}'
        file_name = os.path.basename(path)
        f = open(path, 'r')
        content = f.read()
        f.close()
        dwld_connection.send(f'{file_name}$${content}'.encode())
        dwld_connection.close()
        dwld_socket.close()


file_transfer_protocol = FTP_Server()
