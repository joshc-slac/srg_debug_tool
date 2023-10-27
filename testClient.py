# modified from https://docs.python.org/3/library/socket.html

# Echo client program
import socket
import sys
import argparse


class Client:
    def __init__(self):
        self.HOST = 'localhost'    # The remote host
        self.PORT = 11312              # The same port as used by the server
        self.socket = None
        self.parse_args()
        self.send_msg(self.message)

    def parse_args(self):
        argParser = argparse.ArgumentParser()
        argParser.add_argument("-m", "--message", help="string to send", type=str, dest="message")
        args = argParser.parse_args()

        # application layer logic
        argParser.add_argument("-k", "--kill_serv", help="command to kill server", type=bool)
        argParser.add_argument("-r", "--perform_read", help="command to kill server", type=bool)

        print(args.message)
        self.message = args.message

    def send_msg(self, mess=None):
        for res in socket.getaddrinfo(self.HOST, self.PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.socket = socket.socket(af, socktype, proto)
            except OSError:
                self.socket = None
                continue
            try:
                self.socket.connect(sa)
            except OSError:
                self.socket.close()
                self.socket = None
                continue
            break
        if self.socket is None:
            print('could not open socket')
            sys.exit(1)
        with self.socket:
            if (mess is None):
                self.socket.sendall(b'Hello, world')
            else:
                self.socket.sendall(bytes(mess, "utf-8"))
            data = self.socket.recv(1024)
        print('Received', repr(data))


if __name__ == "__main__":
    c = Client()
