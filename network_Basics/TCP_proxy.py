import sys
import socket
import threading


#Server code
def server_loop(localhost, localport, remote_host, remote_port, receive_first):

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		server.bind((localhost,localport))

	except:
		print("[-] Failed to listen on %s:%d" % (localhost, localport))
		print("[-] Check for other listening sockets or correct permissions")
		sys.exit(0)

	print("[+] Connection Established successfully. Listening on %s:%d" % (localhost, localport))

	server.listen(5)

	while True:
		client_socket, addr = server.accept()

		print("[++] Received incoming connection from %s:%d" % (addr[0], addr[1]))
		proxy_thread = threading.Thread(target=proxy_handler, args = (client_socket, remote_host, remote_port, receive_first))

		proxy_thread.start()

# Proxy handler code
def proxy_handler(client_socket, remote_host, remote_port, should_receive_first):
	remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	remote_socket.connect((remote_host, remote_port))

	if should_receive_first:
		remote_buffer = receive_from(remote_socket)
		hexdump(remote_buffer)

		remote_buffer = response_handler(remote_buffer)

		if len(remote_buffer):
			print ("[<==] Sending %d bytes to localhost." % len(remote_buffer))
			client_socket.send(remote_buffer)

	while True:
		local_buffer = receive_from(client_socket)

		if len(local_buffer):
			print("[==>] Received %d bytes from localhost." % len(local_buffer))
			hexdump(local_buffer)

			local_buffer = request_handler(local_buffer)

			remote_socket.send(local_buffer)
			print("[==>] Sent to remote")
			remote_buffer = receive_from(remote_socket)

			if len(remote_buffer):
				print("[<==] Received %d bytes from remote." % len(remote_buffer))

				remote_buffer = response_handler(remote_buffer)
				client_socket.send(remote_buffer)

				print("[<==] Sent to localhost.")
			if not len(local_buffer) or not len(remote_buffer):
				client_socket.close()
				remote_socket.close()
				print("[-] No more data. Closing connection.")
				break

# hexdump code
def hexdump(src, length=16):
    result = []

    if isinstance(src, bytes):
        src = src.decode(errors="replace")

    for i in range(0, len(src), length):
        word = src[i:i+length]
        hexa = ' '.join([f"{ord(c):02X}" for c in word])
        text = ''.join([c if 0x20 <= ord(c) < 0x7F else '.' for c in word])
        result.append(f"{i:04X}   {hexa:<{length*3}}   {text}")

    print('\n'.join(result))

# Recieve from code
def receive_from(connection):
	buffer = ""

	connection.settimeout(2)

	try:
		while True:
			data = connection.recv(4096)

			if not data:
				break
			else:
				buffer += data
	except:
		pass

	return buffer


# Request handler code
def request_handler(buffer):
	return buffer

# response handler
def response_handler(buffer):
	return buffer



# Main code
def main():
	if len(sys.argv[1:])!=5:
		print("Usage [localhost] [localport] [remotehost] [remoteport][receive_first]\n")
		print("Example: 127.0.0.1 1234 127.0.0.2 1233 True")


	localhost = sys.argv[1]
	localport = int(sys.argv[2])


	remote_host = sys.argv[3]
	remote_port = int(sys.argv[4])

	receive_first = sys.argv[5]

	if "True" in receive_first:
		receive_first = True
	else:
		receive_first = False

	server_loop(localhost,localport,remote_host,remote_port,receive_first)

main()

