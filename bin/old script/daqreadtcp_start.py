import paramiko

nbytes = 4096
hostname = '192.168.137.30'
port = 22
username = 'root' 
password = 'root'
command = './DaqReadTcp'

client = paramiko.Transport((hostname, port))
client.connect(username=username, password=password)

stdout_data = []
stderr_data = []
session = client.open_channel(kind='session')
session.exec_command(command)
while True:
    if session.recv_ready():
        stdout_data.append(session.recv(nbytes))
    if session.recv_stderr_ready():
        stderr_data.append(session.recv_stderr(nbytes))
    if session.exit_status_ready():
        break

#print('exit status: ', session.recv_exit_status())

#print((stdout_data))

session.close()
client.close()
