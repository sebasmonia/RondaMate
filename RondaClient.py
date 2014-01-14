"""
Network client for Ronda Mate based on the chat client found in
http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
"""

__author__ = 'Hoagie'

import socket
import select
from RondaMateCommunication import RondaSocket


class RondaClient():
    """Network client for RondaMate application"""

    def __init__(self, name, host='127.0.0.1', port=3490):
        self.name = name
        self.port = int(port)
        self.host = host
        self.published_rondas = []
        self.my_ronda_members = []
        # Connect to server at port
        try:
            self.sock = RondaSocket((host, self.port))
            self.sock.send('Name=' + self.name)
            data = self.sock.receive()
            print("data is: ", str(data))
            print('Connected to RondaMate server@%d' % self.port)
        except socket.error as e:
            print('Could not connect to the server {0}. Error {1}'.format((self.port, e)))
            self.sock.close()

    def create_ronda(self):
        data = "New ronda=" + self.name
        self.sock.send(data)

    def close_ronda(self):
        data = "Close ronda=" + self.name
        self.sock.send(data)

    def subscribe_to_ronda(self, ronda_name):
        data = "Subscribe=" + self.name + "," + ronda_name
        self.sock.send(data)
        #data = self.sock.receive()
        #if not data == 'OK':
        #    raise Exception('Cannot subscribe to ronda')

    def update(self):
        try:
            self.sock.send("update_rondas")
            self.process_rondas(self.sock.receive())
            self.sock.send("update_members")
            self.process_ronda_members(self.sock.receive())
            return
            # Wait for input from socket
            input_ready, output_ready, except_ready = select.select([self.sock.sock], [], [])
            if input_ready:
                data = self.sock.receive()
                if data is None:
                    print('Shutting down.')
                    self.sock.close()
                elif data.startswith('Rondas='):
                    self.process_rondas(data)
                elif data.startswith('Add member='):
                    self.accept_new_member(data)
                elif data.startswith('Ronda members='):
                    self.process_ronda_members(data)
        except Exception as e:
            print('Interrupted. {0}'.format(e,))
            self.sock.close()

    def close_client(self):
        data = 'Close'
        self.sock.send(data)
        self.sock.close()

    def process_rondas(self, raw_data):
        rondas = raw_data.replace('Rondas=', '')
        rondas = rondas.split(',')
        print("received rondas: ", rondas)
        self.published_rondas = rondas

    def accept_new_member(self, raw_data):
        member_name = raw_data.replace('Add member=', '')
        self.ronda_members.append(member_name)

    def process_ronda_members(self, raw_data):
        member_list = raw_data.replace('Ronda members=', '')
        member_list = member_list.split(',')
        print("received members: ", member_list)
        self.my_ronda_members = member_list

    def test_prompt(self):
        while True:
            print("Listed rondas: ", self.published_rondas)
            print("My members: ", self.my_ronda_members)
            cmd = input("cmd: ")
            if cmd == 'new':
                self.create_ronda()
            elif cmd == 'subs':
                cmd = input('Name to subscribe: ')
                self.subscribe_to_ronda(cmd)
            elif cmd == 'update':
                self.update()
            elif cmd == "quit":
                self.close_client()
                break

if __name__ == "__main__":
    name = input("Set instance name: ")
    client = RondaClient(name, '127.0.0.1', 3490)
    client.test_prompt()
    #client.update()

    #import sys

    #if len(sys.argv) < 3:
    #    sys.exit('Usage: %s chatid host portno' % sys.argv[0])

    #client = RondaClient(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    #client.cmdloop()
