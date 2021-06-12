# Telnet Server and client
This a telnet client and server in python with multiple features

## Features
- Upload a file through telnet protocol
- Execute a command on server terminal
- Send a simple text
- Send an encrypted text through TLS
- Connect to telnet server and keep connection open

# How it works
First we fire up the server.
Server listens on localhost:23 for telnet messages and localhost:2300 for TLS messages
```sh
python server.py
```
Then we can use the client to send messages to server
- Upload a file
```sh
python client.py upload "./client_files/hello.txt" localhost 23
```
- Execute a command on server terminal
```sh
python client.py exec "dir" localhost 23
```
- Send a text
```sh
python client.py send "hello" localhost 23
```
- Send an encrypted text
```sh
python client.py send -e "hello" localhost 2300
```
- Connect to telnet server
```sh
python client.py connect www.google.com 80
```
then we can send a GET request after connection being made:
```sh
GET / HTTP/1.1
```

We can also see the command history:
```sh
python client.py history
```