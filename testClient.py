# modified from https://docs.python.org/3/library/socket.html

# echo client program
import socket
import sys
import argparse

from SRGTesterJobs import SrgTesterJobType


class client:
  def __init__(self):
    self.HOST = 'localhost'    # the remote host
    self.PORT = 11312              # the same port as used by the server
    self.socket = None
    if (not self.parse_args()):  # populates self.message
      print("Error returning without sending command")
      return 
    self.send_msg(self.message)

  def parse_args(self):
    '''
    Parse args submitted to client
    Returns boolean: if True clear to proceed, if False user requested configuration is dangerous or not well defined
    '''
    argparser = argparse.ArgumentParser()

    # Application layer args
    argparser.add_argument("-k", "--kill_serv", help="command to kill server", type=bool)
    argparser.add_argument("-r", "--perform_unarmed_read", 
                           help="command to perform 'unarmed' read, does not actuate failure cond", type=bool, dest="perform_unarmed_read")
    argparser.add_argument("-x", "--perform_armed_read", 
                           help="command to perform armed read, warning this could induce dropping the ball when run on prod tooling", 
                           type=bool, dest="perform_armed_read")
    args = argparser.parse_args()

    # Application layer arg parsing
    if (args.perform_unarmed_read and args.perform_armed_read):
      print("Error: cannot specify both armed and unarmed reads -r and -x are mutually exclusive")
      return False
    elif (args.perform_unarmed_read):  
      self.message = SrgTesterJobType.PERFORM_UNARMED_READING
    elif (args.perform_armed_read):
      self.message = SrgTesterJobType.PERFORM_ARMED_READING
    return True

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
        self.socket.sendall(b'hello, world')
      else:
        self.socket.sendall(bytes(f"{int(mess)}", "utf-8"))  # TODO(josh): int to stringification is dumb,prod machines don't support StrEnum type  protobuf-ize
      data = self.socket.recv(1024)
    print('received', repr(data))


if __name__ == "__main__":
  c = client()
