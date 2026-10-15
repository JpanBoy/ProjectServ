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
    PLAYER_UPDATE = 0x14
    DISCONNECT = 0x1f

class ConnectionState(Enum):
    LOGIN = 1
    CONNECTED = 2
    DISCONNECT = 3

class Player:
    def __init__(self, name, sock, posX, posY, cli_id):
        self.name = name
        self.sock = sock
        self.posX = posX
        self.posY = posY
        self.client_id = cli_id
 
players = {}
client_id = 0
client_name = ""
client_pos = [0,0]
def recv_exact(client, byte):
    data = b''
    while len(data) < byte:
        chunk = client.recv(byte - len(data))
        data += chunk
    return data

def recv_msg(client):
    player = None
    global client_id
    while True:
        packet_id, payload = recv_packet(client)
        if packet_id == bytes([ClientPacket.LOGIN]):
            name = payload.decode()
            client_id += 1
            player = Player(name, client, 0, 0, client_id)
            players[client_id] = player
            send_packet(client, f"Login Accepted: {player.name}", bytes([ServerPacket.LOGIN_SUCCESS]))

        elif packet_id == bytes([ClientPacket.MOVE]):
            if player is None:
                continue
            x, y = map(int, payload.decode().split())
            player.posX = x
            player.posY = y
            send_packet(client, f"Moved player to ({x}, {y})", bytes([ServerPacket.CHAT]))
            print(f"Moved {player.name} to {x} {y}")

        elif packet_id == bytes([ClientPacket.DISCONNECT]):
            send_packet(client, f"", bytes([ServerPacket.DISCONNECT]))
            players.pop(player.client_id, None)
            broadcast(f"{player.name} has left", "Server")
            break

        elif packet_id == bytes([ClientPacket.CHAT]):
            if player is not None:
                print(f"[{player.name}] {payload.decode()}")
                broadcast(payload.decode(), player.name)

    client.close()

def send_message(client):
    while True:
        send_msg = input("")
        send_packet(client, send_msg, bytes([ServerPacket.CHAT]))

def broadcast(msg, sender):
    for player in list(players.values()):
        send_packet(player.sock, f"[{sender}] {msg}", bytes([ServerPacket.CHAT]))

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

def handler(client):
    pass

def terminal():
    while True:
        serv_inp = input()
        if serv_inp.startswith("/"):
            parts = serv_inp.split()
            command = parts[0]
            if command == "/bc":
                if len(parts) == 1:
                    print("Invalid Format")
                else:
                    msg = serv_inp.split(None, 1)[1]
                    broadcast(msg, "Server")
            if command == "/closeserver":
                if len(parts) == 1:
                    print("Closing the server")
        else:
            print("[Warning] Please input a valid command starting with /")
        
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("127.0.0.1", 5000))
server.listen()

print("Server waiting for connection")
threading.Thread(target=terminal).start()
while True:
    client, address = server.accept()
    print(f'{address} has connected')
    threading.Thread(target=recv_msg, args=(client,)).start()

# while True:
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
#     print(f'[Client] {msg}')

#     send_msg = input()
#     send_header = struct.pack("!I", len(send_msg))
#     send_payload = send_msg.encode()
#     message = send_header + send_payload
#     client.sendall(message)
#     if send_msg == "exit":
#         break

# recv_th = threading.Thread(target=recv_msg, args=(client,))
# send_th = threading.Thread(target=send_message, args=(client,))

# recv_th.start()
# send_th.start()

# recv_th.join()
# send_th.join()

# client.close()
# server.close()
