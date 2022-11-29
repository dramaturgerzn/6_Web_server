import socket
import datetime as dt
import threading
from threading import Thread
from settings import Settings
import os


addr = None
t_lock = threading.Lock()
flag = 0

def connection():
    global addr
    global flag
    with t_lock:
        conn, addr = server.accept()
        addr_cpy = addr
    log_file.write(f"{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')}; ADDRESS {addr_cpy} CONNECTED!\n")
    while True:
        try:
            data = conn.recv(Settings.size)
            msg = data.decode()
            #print(msg)
            conn.send(load_page(msg))
            # print(f"Разорвано соединение с {addr_cpy}\n")

        except ConnectionAbortedError:
            log_file.write(f"{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')}; ADDRESS {addr_cpy} DISCONNECTED...\n")
            with t_lock:
                flag = 1
            break


def load_page(request):
    global flag
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
    header_404 = 'HTTP/1.1 404 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
    temp_path = ''
    try:
        _, path = request.split(' ')[:2]
        temp_path = path
    except ValueError:
        path = temp_path
    date = dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')
    content_type = 'Content-type: text/html; '
    con = 'Connection: alive '
    try:
        with open(path[1:], 'rb') as file:
            response = file.read()
            log_file.write(f"{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')}; ADDRESS: {addr}; REQUESTED FILE: {path}; ERROR: -\n")
            return header.encode() + response + date.encode() + '; '.encode() + 'Server: '.encode() + Settings.name.encode() + content_type.encode() + con.encode()
    except FileNotFoundError:
        if flag == 0:
            log_file.write(f"{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')}; ADDRESS: {addr}; REQUESTED FILE: {path}; ERROR: 404. File not found!\n")
        return header_404.encode() + 'Page not found! error 404! '.encode() + date.encode() + '; '.encode() + 'Server: '.encode() + Settings.name.encode() + content_type.encode() + con.encode()


if __name__ == '__main__':
    if not('logs.txt' in os.listdir()):
        log_file = open('logs.txt', 'w')
    else:
        log_file = open('logs.txt', 'a')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', Settings.port))
    log_file.write(f"{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')}; Server started. Listening to port: {Settings.port}\n")
    print(f"Listening to port: {Settings.port}")
    server.listen(5)

    threads = [threading.Thread(target=connection) for i in range(Settings.num_clients)]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    log_file.write(f"{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT+3')}; Server CLOSED!\n")
    server.close()
    log_file.close()
