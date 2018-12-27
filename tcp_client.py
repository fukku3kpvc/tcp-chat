import socket
import sys
import os
import time
from threading import Thread


def is_non_zero_file(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def listening():
    while True:
        reply = sock.recv(65536)
        if reply == b'/q':
            print('Exiting from server...')
            sock.shutdown(socket.SHUT_WR)
            sock.close()
            os._exit(1)
        if reply == b'/d':
            print('Downloading file...')
            break
        print(reply.decode())


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 20113))
Thread(target=listening).start()
ext = 1
while True:
    msg = input()
    try:
        if msg == '/f':
            sock.sendall(msg.encode())
            file_path = input('Enter file path to upload: ')
            sock.sendall(file_path.encode())
            with open(file_path, 'rb') as f:
                l = f.read(65536)
                while l:
                    time.sleep(0.1)
                    sock.sendall(l)
                    l = f.read(65536)
                sock.send('EOF'.encode())
                print('File uploaded successfully')
            f.close()
            continue
    except Exception as e:
        print('ERROR: traceback in message %s, skipping', e)
        pass
    try:
        if msg == '/d':
            sock.sendall(msg.encode())
            file_ext = sock.recv(65536)
            file_path = 'received_file' + file_ext.decode()
            if os.path.isfile('received_file' + file_ext.decode()):
                file_path = 'received_file' + str(ext) + file_ext.decode()
                ext += 1
            with open(file_path, 'wb') as f:
                i = 1
                while True:
                    data = sock.recv(65536)
                    if data == b'EOF':
                        if i == 1:
                            print('File is empty!')
                        break
                    f.write(data)
                    i += 1
                if i is not 1:
                    print('Download complete!')
                f.close()
                Thread(target=listening).start()
                continue
    except Exception as e:
        print('ERROR: traceback in message %s, skipping', e)
        pass
    sock.sendall(msg.encode())
    sys.stdout.write("\033[F")  # back to previous line
    sys.stdout.write("\033[K")  # clear line
