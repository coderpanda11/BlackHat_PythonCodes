import socket
import threading

ip = "0.0.0.0"
port = 3557

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((ip, port))

server.listen(5)

print("[*] Listening on the %s:%d" % (ip,port))

#client handling thread
def handle_client(client_socket):
	#printing what client sends
	request = client_socket.recv(1024)

	print("[*] Recieved: %s" % request)

	#send back a packet
	handshake = "This is a TCP server"
	client_socket.send(handshake.encode())

	client_socket.close()

while True:
	client, addr = server.accept()
	print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

	# spin up our client thread to handle incoming data
	client_handler = threading.Thread(target=handle_client,args=(client,))
	client_handler.start()
