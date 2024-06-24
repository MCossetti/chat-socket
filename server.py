import socket
import threading
import colorama
from colorama import Fore, Style
import sys

colorama.init()

# Connection Data

host = input("Choose Server IP: ")
port = int(input("Choose Server Port Number: "))

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []
rooms = {}
colors = {}  # Dictionary to store colors for each nickname
available_colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

# Sending Messages To All Connected Clients
def broadcast(message, room):
    for client in rooms[f'{room}']:
       try:
            client.send(message)
       except Exception as e:
            print(f"Error broadcasting to client: {e}")
            handle_disconnect(client)
 

# Find the room of the client
def getRoom(client):
    for room in rooms:
        if client in rooms[f'{room}']:
            return room

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024).decode('utf-8')
            if not message:
                handle_disconnect(client)
                break
            room = getRoom(client)
            nickname = nicknames[clients.index(client)]
            color = colors[nickname]
            colored_message = "{}{}{}".format(color, message, Style.RESET_ALL)
            broadcast(colored_message.encode('utf-8'), room)
        except OSError as e:
            print(f"(OSError: {e})")
            handle_disconnect(client)
            break
        except ConnectionResetError as e:
            print(f"ConnectionResetError: Client {client} disconnected unexpectedly.")
            handle_disconnect(client)
            break
        except Exception as e:
            print(f"Error: {e}")
            handle_disconnect(client)
            break


def handle_disconnect(client):
    try:
        index = clients.index(client)
        clients.remove(client)
        room = getRoom(client)
        
        # Remove client from room list
        if room in rooms and client in rooms[room]:
            rooms[room].remove(client)

        client.close()
        nickname = nicknames[index]
        broadcast('{}{} left!{}'.format(colors[nickname], nickname, Style.RESET_ALL).encode('utf-8'), room)
        print(f"{nickname} left room {room}")
        nicknames.remove(nickname)
        colors.pop(nickname)
    except ValueError:
        pass  # If client is already removed or isn't in the list


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        
        # Assign a color to the nickname
        color = available_colors[len(colors) % len(available_colors)]
        colors[nickname] = color

        # Request and Store Room
        client.send('ROOM'.encode('utf-8'))
        room = client.recv(1024).decode('utf-8')
        
        #Test if dictionary key exists, if not: creates it
        try: 
            rooms[f'{room}'].append(client)
        except KeyError: 
            rooms[f'{room}']=[client]

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{}{} joined room {}!{}".format(color, nickname, room, Style.RESET_ALL).encode('utf-8'), room)
        client.send('Connected to server!'.encode('utf-8'))
        print("Rooms: {}".format(rooms))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == '__main__':
    receive()
