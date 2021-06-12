import socket
import threading
import sys
import time
import ssl
import ntpath


def connectTo(hostname, p):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
        print("Connected to remote host")
        return s
    except ConnectionError:
        print("Unable to connect")
        exit(0)


def reader(s, times=0):
    flag = 1
    if times > 0:
        flag = 0

    i = 0
    while i < times or flag:
        try:
            data = s.recv(4096).decode('latin-1')
            if not data:
                print('Connection closed')
                sys.exit()
            else:
                sys.stdout.write(data)
        except socket.timeout:
            time.sleep(0.5)
            continue
        except ConnectionResetError:
            print('Connection closed')
            sys.exit()
        i += 1


def writer(s):
    while 1:
        try:
            msg = sys.stdin.readline()
            s.send(msg.encode('ascii'))
        except socket.error:
            print("Writer thread shutdown.")
            s.clos()
            exit(0)


def scanPorts(hostname, begin, end):
    ipv4 = socket.gethostbyname(hostname)
    print("Scanning open ports")
    print("*" * 20)
    print ("Host: {} \nIP: {}".format(hostname, ipv4))
    print("*" * 20)
    try:
        for p in range(begin, end + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)
            result = s.connect_ex((ipv4, p))
            if result == 0:
                print("Port {:< 10d} --- open".format(p))
            else:
                print("Port {:< 10d} -   closed".format(p))
            s.close()

    except KeyboardInterrupt:
        print("Scanning stopped.")
        sys.exit()
    except socket.gaierror:
        print("Hostname could not be resolved.")
        sys.exit()
    except socket.error:
        print("Server not responding.")
        sys.exit()

    print("*" * 20)
    print("Finished.")


def saveHistory(history):
    with open("./history/history.txt", "a") as file:
        file.write(" ".join(history))
        file.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: enter command.")
        sys.exit()
    if sys.argv[1] == "connect":
        if len(sys.argv) < 4:
            print("Error: Enter hostname and port.")
            sys.exit()
    elif sys.argv[1] == "scan":
        if len(sys.argv) < 5:
            print("Error: Enter hostname, starting port and ending port.")
            sys.exit()
    elif sys.argv[1] == "send":
        if sys.argv[2] != "-e" and len(sys.argv) < 5:
            print("Error: Enter message, hostname and port.")
            sys.exit()
        elif sys.argv[2] == "-e" and len(sys.argv) < 6:
            print("Error: Enter message, hostname and port.")
            sys.exit()
    elif sys.argv[1] == "upload":
        if len(sys.argv) < 5:
            print("Error: Enter file path, hostname and port.")
            sys.exit()
    elif sys.argv[1] == "exec":
        if len(sys.argv) < 5:
            print("Error: Enter command, hostname and port.")
            sys.exit()
    elif sys.argv[1] == "history":
        pass
    else:
        print("Error: Something went wrong.")

    if sys.argv[1] == "connect":
        host = sys.argv[2]
        port = int(sys.argv[3])
        sock = connectTo(host, port)

        readerThread = threading.Thread(target=reader, name='reader', args=(sock,))
        writerThread = threading.Thread(target=writer, name='writer', args=(sock,))

        readerThread.start()
        writerThread.start()

        readerThread.join()
        writerThread.join()
        saveHistory([sys.argv[1], sys.argv[2], sys.argv[3]])
    elif sys.argv[1] == "scan":
        scanPorts(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
        saveHistory([sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]])
        exit(0)
    elif sys.argv[1] == "send" and sys.argv[2] != "-e":
        host = sys.argv[3]
        port = int(sys.argv[4])
        sock = connectTo(host, port)
        sock.send("send    ".encode("ascii"))
        print("Sending message: {}".format(sys.argv[2]))
        sock.send(sys.argv[2].encode("ascii"))
        sock.send("\r\n\r\n".encode())
        print("Receiving:")
        print("-" * 10)
        reader(sock, 1)
        print("\n" + ("-" * 10))
        sock.close()
        saveHistory([sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]])
    elif sys.argv[1] == "send" and sys.argv[2] == "-e":
        host = sys.argv[4]
        port = int(sys.argv[5])

        if port != 2300:
            print("Port 2300 is valid for tls.")
            sys.exit()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ssock = ssl.wrap_socket(sock)
        ssock.connect((host, port))

        print("Sending message: {}".format(sys.argv[3]))
        ssock.send(sys.argv[3].encode())
        ssock.send("\r\n\r\n".encode())
        print("Receiving:")
        print("-" * 10)
        reader(ssock, 1)
        print("\n" + ("-" * 10))
        ssock.close()
        saveHistory([sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]])
    elif sys.argv[1] == "upload":
        data = ""
        try:
            with open(sys.argv[2], "rb") as f:
                byte = f.read()
                data = byte.decode()
        except FileNotFoundError as e:
            print("Error: Couldn't find file.")
            sys.exit()
        host = sys.argv[3]
        port = int(sys.argv[4])
        sock = connectTo(host, port)
        sock.send("upload  ".encode("ascii"))
        head, tail = ntpath.split(sys.argv[2])
        filename = tail or ntpath.basename(head)
        sock.send(("<file>" + filename + "</file>").encode("ascii"))
        sock.send(data.encode("ascii"))
        sock.send("\r\n\r\n".encode())
        print("Receiving:")
        print("-" * 10)
        reader(sock, 1)
        print("\n" + ("-" * 10))
        sock.close()
        saveHistory([sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]])
    elif sys.argv[1] == "exec":
        host = sys.argv[3]
        port = int(sys.argv[4])
        sock = connectTo(host, port)
        sock.send("exec    ".encode("ascii"))
        print("Sending message: {}".format(sys.argv[2]))
        sock.send(sys.argv[2].encode("ascii"))
        sock.send("\r\n\r\n".encode())
        print("Receiving:")
        print("-" * 10)
        reader(sock, 1)
        print("\n" + ("-" * 10))
        sock.close()
        saveHistory([sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]])
    elif sys.argv[1] == "history":
        saveHistory([sys.argv[1]])
        with open("./history/history.txt", "r") as file:
            print("History")
            print("-" * 10)
            while True:
                line = file.readline()
                if not line:
                    break
                print(line, end="")

            print("-" * 10)



