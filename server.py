import socket
import threading
import colorama
from colorama import Fore, Style
import sys
import signal

# Function to handle the SIGINT signal (Ctrl+C)
def signal_handler(sig, frame):
    print("\nProgram interrupted by user.")
    sys.exit(0)

# Set the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

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
        client.send(message)

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
            room = getRoom(client)
            nickname = nicknames[clients.index(client)]
            color = colors[nickname]
            colored_message = "{}{}{}".format(color, message, Style.RESET_ALL)
            broadcast(colored_message.encode('utf-8'), room)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            room = getRoom(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{}{} left!{}'.format(colors[nickname], nickname, Style.RESET_ALL).encode('utf-8'), room)
            nicknames.remove(nickname) 
            colors.pop(nickname)  # Remove color association
            break

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
        
        #Test if dictionary key exists, if it doesn't exists creates it
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

receive()
