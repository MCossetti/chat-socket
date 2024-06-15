import socket
import threading
import sys
import colorama
import signal

# Function to handle the SIGINT signal (Ctrl+C)
def signal_handler(sig, frame):
    print("\nProgram interrupted by user.")
    sys.exit(0)

# Set the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


colorama.init()


#choosing server ip and port
serverip = input("Choose Server IP: ")
serverport = input("Choose Server Port: ")

#converting serverport to integer
serverport = int(serverport)

# Choosing Nickname and room
nickname = input("Choose your nickname: ")
room = input("Choose your room: ")
# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((serverip, serverport))

# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            elif message == 'ROOM':
                client.send(room.encode('utf-8'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break
            
# Sending Messages To Server
def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode('utf-8'))
        
        # message = '{}: {}'.format(room, input(''))
        # client.send(message.encode('utf-8'))
        
        sys.stdout.write("\033[F") # Cursor up one line
        sys.stdout.write("\033[K") # Clear to the end of line
        

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
