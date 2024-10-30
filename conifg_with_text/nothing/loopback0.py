import paramiko
import time

username = 'admin'
password = '123'
IP = '192.168.136.130'

# สร้าง SSH Client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # เชื่อมต่อไปยังอุปกรณ์
    ssh.connect(IP, username=username, password=password)

    # เปิด interactive shell session
    remote_conn = ssh.invoke_shell()

    # รอให้พร้อมใช้งานและส่งคำสั่ง
    time.sleep(1)
    remote_conn.send("en\n")
    time.sleep(1)
    remote_conn.send("123\n")
    time.sleep(1)
    remote_conn.send("conf t\n")
    time.sleep(1)
    remote_conn.send("int lo 10\n")
    time.sleep(1)
    remote_conn.send("ip address 10.10.10.10 255.255.255.255\n")
    time.sleep(1)
    remote_conn.send("end\n")
    time.sleep(1)
    remote_conn.send("exit\n")
    time.sleep(1)

    # อ่านผลลัพธ์ทั้งหมดที่ส่งกลับจากอุปกรณ์
    output = remote_conn.recv(65535).decode('utf-8')
    print(output)

finally:
    # ปิดการเชื่อมต่อ
    ssh.close()
