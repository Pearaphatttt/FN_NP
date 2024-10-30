import paramiko
import threading
import os
import subprocess
import time
import sys
import re

def ip_is_valid():
    global ip_list
    check = True  # สมมติว่า IP ถูกต้องตั้งแต่แรก

    while True:
        print("\n# # # # # # # # # # # # # # # # # # # #\n")
        ip_file = input("# ใส่ชื่อไฟล์ IP และนามสกุล: ")
        print("\n# # # # # # # # # # # # # # # # # # # #\n")

        try:
            # เปิดไฟล์และอ่านรายการ IP
            with open(ip_file, 'r') as f:
                ip_list = f.readlines()

            # ตรวจสอบความถูกต้องของ IP
            for ip in ip_list:
                ip = ip.strip()  # ลบช่องว่างและบรรทัดใหม่
                octets = ip.split('.')

                if (len(octets) == 4 and 
                    1 <= int(octets[0]) <= 223 and 
                    int(octets[0]) != 127 and 
                    not (int(octets[0]) == 169 and int(octets[1]) == 254) and
                    all(0 <= int(octet) <= 255 for octet in octets[1:])):
                    print(f"IP ปัจจุบันที่ตรวจสอบ: {ip}")
                else:
                    print(f"IP ปัจจุบันที่ตรวจสอบ: {ip}")
                    print('\n* พบ IP ที่ไม่ถูกต้อง! กรุณาตรวจสอบและลองใหม่อีกครั้ง!\n')
                    check = False
                    break

            if check:
                print("\nIP ทั้งหมดในไฟล์ได้รับการตรวจสอบแล้วและถูกต้อง")
                break

        except FileNotFoundError as e:
            print(f"*** พบข้อผิดพลาด: {e}")
            print(f"\n*** ไฟล์ {ip_file} ไม่มีอยู่จริง! กรุณาตรวจสอบและลองใหม่!\n")

        except ValueError:
            print("\n* พบข้อผิดพลาดในการแปลงตัวเลข IP! กรุณาตรวจสอบไฟล์ IP\n")

def ping_ip(ip):
    """ฟังก์ชันสำหรับ ping IP เพื่อเช็คการเชื่อมต่อ"""
    try:
        param = '-n' if sys.platform.lower() == 'win32' else '-c'
        response = subprocess.call(['ping', param, '2', ip], stdout=subprocess.DEVNULL)

        if response == 0:
            print(f"อุปกรณ์ {ip} ตอบสนองได้")
            return True
        else:
            print(f"\n* ไม่ได้รับการตอบกลับจากอุปกรณ์ {ip}")
            return False
    except Exception as e:
        print(f"\n* พบข้อผิดพลาดในการ ping: {e}")
        return False

def check_reachability():
    """ตรวจสอบว่า IP ทั้งหมดสามารถ ping ได้หรือไม่"""
    print("\n* กำลังตรวจสอบการเชื่อมต่อ IP... โปรดรอ...\n")
    for ip in ip_list:
        ip = ip.strip()
        if not ping_ip(ip):
            print("* โปรดตรวจสอบอุปกรณ์หรือรายการ IP อีกครั้ง\n")
            return False
    print("\n* อุปกรณ์ทั้งหมดตอบสนองได้ พร้อมเข้าสู่ขั้นตอนถัดไป\n")
    return True

def user_is_valid():
    """ตรวจสอบไฟล์ username/password"""
    global user_file

    while True:
        print("# # # # # # # # # # # # # # # # # # # # #\n")
        user_file = input("# ใส่ชื่อไฟล์ username/password และนามสกุล: ")
        print("# # # # # # # # # # # # # # # # # # # # #\n")

        if os.path.isfile(user_file):
            print("\n* ไฟล์ username/password ถูกต้อง พร้อมดำเนินการขั้นต่อไป...\n")
            break
        else:
            print(f"\n* ไฟล์ {user_file} ไม่มีอยู่จริง! กรุณาตรวจสอบและลองใหม่!\n")

def cmd_is_valid():
    """ตรวจสอบไฟล์คำสั่ง"""
    global cmd_file

    while True:
        print("# # # # # # # # # # # # # # # # # # # # #\n")
        cmd_file = input("# ใส่ชื่อไฟล์คำสั่งและนามสกุล: ")
        print("# # # # # # # # # # # # # # # # # # # # #\n")

        if os.path.isfile(cmd_file):
            print("\n* ไฟล์คำสั่งถูกต้อง กำลังส่งคำสั่งไปยังอุปกรณ์...\n")
            break
        else:
            print(f"\n* ไฟล์ {cmd_file} ไม่มีอยู่จริง! กรุณาตรวจสอบและลองใหม่!\n")

def open_ssh_conn(ip):
    """เชื่อมต่อกับอุปกรณ์ผ่าน SSH และส่งคำสั่ง"""
    try:
        with open(user_file, 'r') as f:
            username, password = f.readline().strip().split(',')

        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(ip, username=username, password=password, allow_agent=False, look_for_keys=False)

        connection = session.invoke_shell()

        with open(cmd_file, 'r') as f:
            for line in f:
                connection.send(line + '\n')
                time.sleep(2)

        output = connection.recv(65535).decode('utf-8')
        print(f"\nผลลัพธ์จากอุปกรณ์ {ip}:\n{output}")

        session.close()

    except paramiko.AuthenticationException:
        print("* ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง! กรุณาตรวจสอบและลองใหม่")

def create_threads():
    """สร้าง thread สำหรับแต่ละ IP"""
    threads = []
    for ip in ip_list:
        ip = ip.strip()
        thread = threading.Thread(target=open_ssh_conn, args=(ip,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# เรียกใช้ฟังก์ชันต่าง ๆ
try:
    ip_is_valid()
    if check_reachability():
        user_is_valid()
        cmd_is_valid()
        create_threads()

except KeyboardInterrupt:
    print("\n\n* โปรแกรมถูกยกเลิกโดยผู้ใช้. กำลังออก...\n")
    sys.exit()
