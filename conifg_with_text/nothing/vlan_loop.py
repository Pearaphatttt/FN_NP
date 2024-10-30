import telnetlib
import time

username = 'admin'
password = '123'
IP = '192.168.136.160'

tn = telnetlib.Telnet(IP)

tn.read_until(b'Username: ')
tn.write(username.encode('ascii') + b'\n')

if password:
    tn.read_until(b'Password: ')
    tn.write(password.encode('ascii') + b'\n')
tn.write(b'en\n')
tn.write(b'123\n')

tn.write(b'conf t\n')

for n in range(2, 10):
    tn.write(b'vlan ' + str(n).encode('ascii') + b'\n')
    tn.write(b'name Python_VLAN' + str(n).encode('ascii') + b'\n')

tn.write(b'end\n')
tn.write(b'exit\n')

print(tn.read_all().decode('ascii'))