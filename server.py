import socket
import threading

# Connection Data
host = '127.0.0.1'
port = 55557

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []
rooms = {}

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
            message = client.recv(1024)
            room = getRoom(client)
            broadcast(message, room)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            room = getRoom(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('utf-8'), room)
            nicknames.remove(nickname)
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
        broadcast("{} joined room {}!".format(nickname,room).encode('utf-8'), room)
        client.send('Connected to server!'.encode('utf-8'))
        print("Rooms: {}".format(rooms))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        

receive()
