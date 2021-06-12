import socket
import threading
import sys
import time
import ssl
import subprocess


def readAll(address, s, mode):
    message = ""
    while 1:
        try:
            data = s.recv(4096).decode(mode)
            if not data:
                print('Connection closed 2')
                print(message)
                sys.exit()
            else:
                message += data
                end = message.find("\r\n\r\n")
                if end != -1:
                    return message[0:end]
        except socket.timeout:
            time.sleep(0.5)
            continue
        except ConnectionResetError:
            print("Connection was forcibly closed by {}".format(address))
            sys.exit()


def send(address, s, mode):
    message = readAll(address, s, 'ascii')
    try:
        s.send(message.encode('ascii'))
        print(mode + "Message sent to {}: ".format(address))
        print("-" * 10)
        print(message)
        print("-" * 10)
    except socket.error:
        print("Could not send message.")


def upload(address, s):
    message = readAll(address, s, 'ascii')
    start = message.find("<file>") + 6
    end = message.find("</file>")
    filename = message[start:end]
    with open("./server_files/" + filename, "w", newline='') as file:
        file.write(message[end + 7:])
    print("File: " + filename + " Received.")
    s.send(("File: " + filename + " Received.").encode("ascii"))


def execute(address, s):
    message = readAll(address, s, 'ascii')
    p = subprocess.Popen(message, shell=True, stdout=subprocess.PIPE)
    subprocess_return = p.stdout.read()
    s.send(subprocess_return.decode('utf-8').encode("ascii"))
    print("Message sent to {}: ".format(address))
    print("-" * 10)
    print(subprocess_return.decode())
    print("-" * 10)


def task(address, s, command):
    if command == "send    ":
        print("Client with address {} asked for {} service".format(address, "send"))
        send(address, s, "")
    elif command == "upload  ":
        print("Client with address {} asked for {} service".format(address, "upload"))
        upload(address, s)
    elif command == "exec    ":
        print("Client with address {} asked for {} service".format(address, "exec"))
        execute(address, s)


def service(address, s):
    while 1:
        try:
            command = s.recv(8).decode('latin-1')
            if not command:
                print("Connection with address: {} closed".format(address))
                print("#" * 20)
                sys.exit()
            else:
                task(address, s, command)
        except socket.timeout:
            time.sleep(0.5)
            continue


def normalThread():
    host = 'localhost'
    port = 23
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
            serverSocket.bind((host, port))
            serverSocket.listen()
            while 1:
                newClientSocket, addr = serverSocket.accept()
                print("#" * 20)
                print("Client with address: {} connected".format(addr))
                newClientThread = threading.Thread(target=service, args=(addr, newClientSocket,))
                newClientThread.start()
    except Exception as e:
        print(e)


def tlsThread():
    host = 'localhost'
    port = 2300
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
            serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sserver = ssl.wrap_socket(serverSocket, server_side=True,
                                      keyfile="./certs/server.key",
                                      certfile="./certs/server.crt")
            sserver.bind((host, port))
            sserver.listen()
            while True:
                connection, address = sserver.accept()
                print("#" * 20)
                print("Client with address: {} connected".format(address))
                send(address, connection, "TLS ")
                connection.close()
                print("Connection with address: {} closed".format(address))
                print("#" * 20)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print("~" * 25)
    print("Server Started")
    print("~" * 25)
    t1 = threading.Thread(target=normalThread, name="t1")
    t2 = threading.Thread(target=tlsThread, name="t2")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
