import paramiko
import time

HOST = '192.168.136.130'
user = 'admin'
password = '123'

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=HOST, username=user, password=password,allow_agent=False,look_for_keys=False)

print("Succentful connected to: "+HOST)


remote_connection = ssh_client.invoke_shell()
remote_connection.send("en\n")
remote_connection.send("123\n")
remote_connection.send("sh ip int brief\n")
time.sleep(1)

output = remote_connection.recv(65535)
print(output.decode('ascii'))

ssh_client.close()