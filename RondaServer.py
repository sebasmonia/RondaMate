"""
Server for Ronda Mate based on the multi client chat server found in
http://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
"""
__author__ = 'Hoagie'

import select
import socket
from RondaMateCommunication import RondaSocket


class RondaMateServer():
    """ Server for RondaMate application """

    def __init__(self, port=3490, backlog=5):
        self.client_sockets = {}
        self.published_rondas = {}
        self.just_started = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', port))
        print('Listening to port', port, '...')
        self.server.listen(backlog)

    def accept_new_client(self):
        python_socket, address = self.server.accept()
        print('Got connection %d from %s' % (python_socket.fileno(), address))
        sock = RondaSocket(a_socket=python_socket)
        # Read the login name
        user_name = sock.receive().replace('Name=','')
        self.just_started = False
        sock.send('OK')
        self.client_sockets[user_name] = sock
        print("Added client: ", user_name)

    def accept_new_ronda(self, raw_data):
        new_ronda = raw_data.replace('New ronda=', '')
        print("Received new ronda: ", new_ronda)
        self.published_rondas[new_ronda] = [new_ronda]

    def accept_new_member(self, raw_data):
        new_member, ronda_name = raw_data.replace('Subscribe=', '').split(',')
        print("received member ", new_member, "for ronda ", ronda_name)

        if ronda_name in self.published_rondas:
            self.published_rondas[ronda_name].append(new_member)

    def close_ronda(self, raw_data):
        ronda_name = raw_data.replace('Close ronda=', '')
        print("Closing ronda: ", ronda_name)

        if ronda_name in self.published_rondas:
            del self.published_rondas[ronda_name]

    def serve(self):
        while True:
            inputs_for_select = [s.sock for s in self.client_sockets.values()]
            inputs_for_select.append(self.server)

            try:
                input_ready, output_ready, except_ready = select.select(inputs_for_select, [], [])
            except select.error as e:
                print("Error in select: {0}".format(e,))
                break
            except socket.error as e:
                print("Error in socket: {0}".format(e,))
                break
            if input_ready:
                #print useful info
                print("Listed rondas: ", self.published_rondas)
                print("Users with sockets: ", self.client_sockets.keys())
                print("Users count: ", len(self.client_sockets))
                print('input_ready length: ', len(input_ready))
            for s in input_ready:
                if s == self.server:
                    # handle the server socket
                    self.accept_new_client()
                else:
                    # handle all other sockets
                    try:
                        for n, rs in self.client_sockets.items():
                            if rs.sock == s:
                                incoming_rs = rs
                                user_name = n
                                data = rs.receive()

                        print("Received from ", user_name, " data ", data)
                        if not data:
                            continue
                        elif data == 'Close':
                            print('Closing client:', user_name)
                            incoming_rs.close()
                            del self.client_sockets[user_name]
                        elif data.startswith("New ronda="):
                            self.accept_new_ronda(data)
                        elif data.startswith('Subscribe='):
                            self.accept_new_member(data)
                        elif data.startswith('Close ronda='):
                            self.close_ronda(data)
                        elif data == 'update_members':
                            info = "Ronda members="
                            if user_name in self.published_rondas:
                                info += ','.join(self.published_rondas[user_name])

                            incoming_rs.send(info)
                        elif data == 'update_rondas':
                            info = "Rondas="
                            info += ','.join(key for key in self.published_rondas.keys())

                            incoming_rs.send(info)
                        else:
                            print("don't know what to do with this:", data)
                    except socket.error as e:
                        # Remove
                        for n, rs in self.client_sockets.items():
                            if rs.sock == s:
                                key = n
                        del self.client_sockets[key]
                        print("Error reading socket", e)

            #break the loop if the last client disconnects
            if not self.client_sockets and not self.just_started:
                break

        self.server.close()

if __name__ == "__main__":
    RondaMateServer().serve()
