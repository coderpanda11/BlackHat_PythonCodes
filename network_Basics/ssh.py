import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(ip, username = user, password = passwd)
	ssh_session = client.get_transport().open_session()
	if ssh_session.active:
		print("Connection Successfull\n")
		command = input("Enter your command: ")
		ssh_session.exec_command(command)
		print(ssh_session.recv(1024).decode())
	return


ssh_command('172.19.41.105', 'kalki', 'sid11151926')