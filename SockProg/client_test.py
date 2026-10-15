import socket
import struct
import threading
from enum import IntEnum
from enum import Enum
class ClientPacket(IntEnum):
    CHAT = 0x01
    LOGIN = 0x02
    MOVE = 0x03
    DISCONNECT = 0x04

class ServerPacket(IntEnum):
    CHAT = 0x11
    LOGIN_SUCCESS = 0x12
    LOGIN_FAILED = 0x13
    DISCONNECT = 0x1f

running = threading.Event()
running.set()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
name = input("Enter name: ")
client.connect(("127.0.0.1", 5000))
def recv_exact(client, byte):
    data = b''
    while len(data) < byte:
        chunk = client.recv(byte - len(data))
        data += chunk
    return data

def recv_msg(client):
    while running.is_set():
        packet_id, msg = recv_packet(client)
        msg = msg.decode()
        if packet_id == bytes([ServerPacket.CHAT]):
            print(msg)
        if packet_id == bytes([ServerPacket.DISCONNECT]):
            running.clear()
            break

def send_message(client):
    while running.is_set():
        send_msg = input("")

        if send_msg.startswith('/'):
            parts = send_msg.split()
            command = parts[0]

            if command == "/move":
                if len(parts) != 3:
                    print("Invalid Format")
                    continue

                try:
                    x = int(parts[1])
                    y = int(parts[2])
                except ValueError:
                    print("Invalid Format")
                    continue

                send_msg = f"{x} {y}"
                packet_id = bytes([ClientPacket.MOVE])

            elif command == "/disconnect":
                if len(parts) != 1:
                    print("Invalid Format")
                    continue

                packet_id = bytes([ClientPacket.DISCONNECT])
                send_msg = ""

            else:
                print("Unknown command")
                continue

        else:
            packet_id = bytes([ClientPacket.CHAT])

        send_packet(client, send_msg, packet_id)

        if packet_id == bytes([ClientPacket.DISCONNECT]):
            running.clear()
            break

def login(client, name):
    send_packet(client, name, b'\x02')

    packet_id, msg = recv_packet(client)
    msg = msg.decode()
    if packet_id == b'\x12':
        print(f'[Server] {msg}')
    else:
        print(f'[Server] Login Failed')

def send_packet(sock, msg, id):
    send_payload = msg.encode()
    send_header = struct.pack("!I", len(send_payload))
    sock.sendall(send_header + id + send_payload)

def recv_packet(sock):
    header = recv_exact(sock, 4)
    length = struct.unpack("!I", header)[0]

    packet_id = recv_exact(sock, 1)
    payload = recv_exact(sock, length)

    return packet_id, payload
# while True:
#     data = input()
#     header = struct.pack("!I", len(data))
#     payload = data.encode()
#     client.sendall(header + payload)
#     if data == "exit":
#         break
#     print(f'[Client] {data}')

#     header = recv_exact(client, 4)
#     length = struct.unpack("!I", header)[0]
#     msg = b''
#     while length > 0:
#         data = client.recv(1024)
#         length -= len(data)
#         msg += data
#     msg = msg.decode()
#     if msg == "exit":
#         break
#     print(f'[Server] {msg}')

login(client, name)
send_th = threading.Thread(target=send_message, args=(client,))
recv_th = threading.Thread(target=recv_msg, args=(client,))

send_th.start()
recv_th.start()

send_th.join()
recv_th.join()

client.close()