import sys
import socket
import getopt
import threading
import subprocess

#Global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

# Main usage function
def usage():
	print("BHP Net Tool\n")
	print("Usage: netcat.py -t target_host -p port")
	print("-l --listen               - listen on [host]:[port] for incoming connections")
	print("-e --execute=file_to_run  - execute the given file upon receiving a connection")
	print("-c --command              - initialize a command shell")
	print("-u --upload=destination   - upon receiving connection upload a file and write to [destination]\n\n")
	print("Examples:\n")
	print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
	print("netcat.py -t 192.168.0.1 -p 5555 -l -u=/home/kali/Desktop/target.exe")
	print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
	sys.exit(0)


# client side code
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break

            print(response, end='')

            buffer = input("")
            buffer += "\n"

            client.send(buffer.encode())

    except Exception as e:
        print(f"[*] Exception! Exiting... {str(e)}")
        client.close()



# the server code
def server_loop():
	global target

	# if no target is defined, we listen on all interfaces
	if not len(target):
		target = "0.0.0.0"

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target,port))
	server.listen(5)
	print(f"[*] Listening on {target}:{port}")

	while True:
		client_socket, addr = server.accept()

		client_thread = threading.Thread(target=client_handler, args = (client_socket,))
		client_thread.start()

def run_command(command):
	command = command.rstrip()

	try:
		output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

	except:
		output = "Failed to execute command.\r\n"

	# send the output back to the client
	return output


# code of client_handler
def client_handler(client_socket):
	global upload
	global execute
	global command

	# check for upload
	if len(upload_destination):
		file_buffer = ""

		while True:
			data = client_socket.recv(1024)

			if not data:
				break
			else:
				file_buffer += data

	# now we take these bytes and try to write them out

	try:
		file_descriptor = open(upload_destination,"wb")
		file_descriptor.write(file_buffer)
		file_descriptor.close()

		client.socket.send("Successfully saved file to %s\r\n" % upload_destination)

	except:
		client_socket.send("Failed to save file to destination".encode())


	# checking for commands

	if len(execute):

		output = run_command(execute)
		client_socket.send(output)

	# if a command shell was requested

	if command:
		while True:
			client_socket.send("\n<Kalki:#> ".encode())

			cmd_buffer = b""
			while b"\n" not in cmd_buffer:
				cmd_buffer += client_socket.recv(1024)

			response = run_command(cmd_buffer)

			client_socket.send(response)


# the main function
def main():
	global listen
	global port
	global execute
	global command
	global upload_destination
	global target

	if not len(sys.argv[1:]):
		usage()

	#reading the commandline options
	try:
		opts, args = getopt.getopt(
    sys.argv[1:],
    "hle:t:p:cu:",
    ["help", "listen", "execute=", "target=", "port=", "command", "upload="]
)

	except getopt.GetoptError as err:
		print(str(err))
		usage()


	for o,a in opts:
		if o in ("-h","--help"):
			usage()
		elif o in ("-l","--listen"):
			listen = True
		elif o in ("-e","--execute"):
			execute = a
		elif o in ("-c","--command"):
			command = True
		elif o in ("-u", "--upload"):
			upload_destination = a
		elif o in ("-t","--target"):
			target = a
		elif o in ("-p", "--port"):
			port = int(a)
		else:
			assert False, "Unhandled option"


	# listening or just sending data
	if not listen and len(target) and port > 0:

		# read in the buffer from the commandline whis will block, so send CTRL-D if not sending input to stdin
		buffer = sys.stdin.read()

		# send data off 
		client_sender(buffer)


	if listen:
		server_loop()


main()

	
