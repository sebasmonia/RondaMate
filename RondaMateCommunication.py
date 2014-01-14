import socket


class RondaSocket:

    def __init__(self, address_port=None, a_socket=None):
        if a_socket is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(address_port)
        else:
            self.sock = a_socket

    def send(self, string_message):
        size = len(string_message)
        if size >= 256:
            raise ValueError("Message is too long.")

        #print("sending size", size, " as ", size.to_bytes(1, "big"))
        self.sock.send(size.to_bytes(1, "big"))
        #print("sending msg", string_message, " as ", bytes(string_message, "ascii"))
        self.sock.sendall(bytes(string_message, "ascii"))

    def receive(self):
        size = self.sock.recv(1)
        size = int.from_bytes(size, "big")
        #print("received size: ", size)

        if size == 0:
            return None

        buf = self.sock.recv(size)
        #print("received in buf: ", buf)

        while len(buf) < size:
            buf += self.sock.recv(size - len(buf))
            #print("received in buf: ", buf)

        #print("returning buf: ", buf.decode('ascii'))
        return buf.decode('ascii')

    def close(self):
        self.sock.close()
        #self.sock.shutdown()