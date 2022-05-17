from socket import *


class FTP_Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(('127.0.0.1', 2121))
        self.prefix_location = self.client.recv(1024).decode()
        self.location = ''
        self.help()

    def get_command(self):
        while True:
            command = input('input : ')
            if command.upper() == 'HELP':
                self.help()
            elif command.upper() == 'LIST':
                self.list()
            elif command.startswith(('DWLD ', 'dwld ')):
                self.dwld(command[5:])
            elif command.upper() == 'PWD':
                print(self.pwd() + '\n')
            elif command.startswith(('CD ', 'cd ')):
                print(self.cd(command[3:]))
            elif command.upper() == 'QUIT':
                self.quit()
            else:
                print('Invalid input!\n')

    def help(self):
        print('\nHELP          : Show help')
        print('LIST          : Show all files and folders')
        print('DWLD filePath : Download a file in specific path')
        print('PWD           : Print working directory')
        print('CD dirName    : Change directory to specific path')
        print('QUIT          : Quit command\n')
        self.get_command()

    def pwd(self):
        return self.location if self.location else '\\'

    def list(self):
        self.client.send(self.pwd().encode())
        response = self.client.recv(16384).decode()
        print(response)

    def cd(self, dest):
        curr_location = self.location
        paths = [-1, *[i for i in range(len(dest))
                       if dest.startswith('\\', i)], len(dest)]

        for i in range(len(paths)-1):
            next_dest = dest[paths[i]+1:paths[i+1]]
            if next_dest == '..' and not self.location:
                return 'The destination is unauthorized.\n'
            elif next_dest == '..':
                curr_location = (curr_location)[:curr_location.rfind('\\')]
            else:
                curr_location += '\\' + next_dest

        self.client.send(('.' + curr_location).encode())
        response = self.client.recv(16384).decode()
        if response == 'True':
            self.location = curr_location
            return self.pwd() + '\n'
        else:
            return 'The system cannot find the path specified.\n'

    def quit(self):
        self.client.send('!close'.encode())
        self.client.close()
        quit()

    def dwld(self, path):
        self.client.send((f'dwld {self.location}\{path}').encode())
        port_number = int(self.client.recv(1024).decode())
        if port_number:
            dwld_client = socket(AF_INET, SOCK_STREAM)
            dwld_client.connect(('127.0.0.1', port_number))
            file = dwld_client.recv(1048576).decode()
            dwld_client.close()
            file_name = file[:file.find('$$')]
            file_content = file[file.find('$$')+2:]
            f = open(file_name, 'w')
            f.write(file_content)
            f.close()
            print('Downloaded successfully\n')
        else:
            print('No such file or directory.\n')


file_transfer_protocol = FTP_Client()
