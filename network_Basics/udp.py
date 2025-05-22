import socket

target_host = "127.0.0.1"
target_port = 80


#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#sending data
data = "AAAAAABBBBCCCC"
client.sendto(data.encode(),(target_host, target_port))

#recieve data
data, addr = client.recvfrom(4096)


print(data, addr)