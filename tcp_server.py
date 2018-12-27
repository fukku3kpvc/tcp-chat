import threading
import socket
import logging
import os
import time


class TCPServer:

    def __init__(self):
        logging.info('Creating TCP Server on port 20113')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('localhost', 20113))
        logging.info('SERVER STATUS: READY')
        self.clients_list = []
        self.active_clients = 0
        self.sock.listen(10)
        self.sock.settimeout(5)
        self.server_status = 'LIVE'
        self.buffer_file = False
        self.file_ext = ''

    def listener(self):
        while self.server_status == 'LIVE':
            try:
                conn, addr = self.sock.accept()
                logging.info('User %s connected', addr)
                self.clients_list.append(conn)
                self.active_clients += 1
                conn.sendall('Hi! Welcome to our server!'.encode())
                self.talk_to_clients((str(addr[1]) + ' joined').encode(), conn, addr)
            except socket.timeout:
                continue
            else:
                t = threading.Thread(target=self.chat, args=(conn, addr))
                t.start()
        self.sock.close()

    @staticmethod
    def is_non_zero_file(path):
        return os.path.isfile(path) and os.path.getsize(path) > 0

    def chat(self, conn, addr):
        logging.info('CONN = %s | ADDR = %s', conn, addr)
        while True:
            try:
                msg = conn.recv(65536)
            except:
                break
            logging.info('msg from %s = %s', addr, msg)
            if msg == b'/q':
                conn.sendall('/q'.encode())
                self.active_clients -= 1
                self.clients_list.remove(conn)
                self.talk_to_clients((str(addr[1]) + ' left this chat').encode(), conn, addr)
                logging.info('User %s left the server', addr)
                conn.close()
                if self.active_clients == 0:
                    logging.info('No active users. Stopping server...')
                    self.server_status = 'DEAD'
                    if os.path.isfile('buffer_file' + self.file_ext):
                        logging.info('Removing buffer file')
                        os.remove('buffer_file' + self.file_ext)
                    break
                continue
            elif msg == b'/f':
                if self.buffer_file:
                    logging.info('Deleting buffer file...')
                    os.remove('buffer_file' + self.file_ext)
                file_path = conn.recv(65536)
                file_name, self.file_ext = os.path.splitext(file_path.decode())
                with open('buffer_file' + self.file_ext, 'wb') as f:
                    while True:
                        data = conn.recv(65536)
                        if data == b'EOF':
                            break
                        f.write(data)
                        logging.info('File uploaded')
                self.buffer_file = True
                f.close()
                logging.info('File closed')
                continue
            elif msg == b'/d':
                b = self.is_non_zero_file('buffer_file' + self.file_ext)
                conn.sendall('/d'.encode())
                conn.sendall(self.file_ext.encode())
                if b:
                    with open('buffer_file' + self.file_ext, 'rb') as f:
                        l = f.read(65536)
                        while l:
                            time.sleep(0.1)
                            conn.sendall(l)
                            l = f.read(65536)
                            logging.info('File transferred')
                    f.close()
                    logging.info('File closed')
                    conn.sendall('EOF'.encode())
                    continue
                else:
                    conn.sendall('EOF'.encode())
                    continue
            elif msg == b'/h':
                conn.sendall('/h - prints command list\n'
                             '/f - upload file\n'
                             '/d - download file\n'
                             '/q - exit from chat'.encode())
                continue
            elif msg.decode()[0] == '/':
                conn.sendall('Unknown command! Type /h for command list'.encode())
                continue
            conn.sendall('<You>: '.encode() + msg)
            self.talk_to_clients(msg, conn, addr)

    def talk_to_clients(self, msg, sender, addr):
        try:
            for i in range(len(self.clients_list)):
                print(self.clients_list[i])
                if sender == self.clients_list[i]:
                    continue
                else:
                    try:
                        self.clients_list[i].sendall(str(addr[1]).encode() + ' >> '.encode() + msg)
                    except:
                        logging.info('REMOVING CLIENT %s', self.clients_list[i])
                        try:
                            self.clients_list.remove(self.clients_list[i])
                            self.active_clients -= 1
                        except:
                            continue
                        continue
        except:
            pass


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    a = TCPServer()
    a.listener()
