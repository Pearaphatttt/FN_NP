import threading
from netmiko import ConnectHandler
import re

# กำหนดข้อมูลเข้าสู่ระบบและช่วง IP ของ switch
username = 'admin'
password = '123'
enable_password = '123'  # รหัสผ่าน enable

ip_start, ip_end = 114, 116
switch_ips = [f"90.90.126.{i}" for i in range(ip_start, ip_end + 1)]

# ฟังก์ชันสำหรับรับข้อมูล VLAN ต้นทาง, VLAN ปลายทาง และ interfaces จากผู้ใช้
def get_user_input():
    source_vlan = input("Enter the current VLAN ID of the interfaces: ")
    target_vlan = input("Enter the target VLAN ID to move interfaces to: ")
    interfaces = input("Enter the Ethernet interfaces to configure (e.g., 0/1-0/5 or 0/2, 0/3): ")
    
    # แปลงข้อมูล interfaces เป็นรายการของ interfaces
    interfaces_list = []
    for part in interfaces.split(","):
        part = part.strip()
        
        # ตรวจสอบว่าเป็นช่วงหรือไม่ เช่น 0/1-0/5
        if "-" in part:
            match = re.match(r"(\d+)/(\d+)-\d+/(\d+)", part)
            if match:
                slot = match.group(1)  # ตัวเลขข้างหน้า "/"
                start = int(match.group(2))  # หมายเลขเริ่มต้น
                end = int(match.group(3))  # หมายเลขสิ้นสุด
                interfaces_list.extend([f"Ethernet{slot}/{i}" for i in range(start, end + 1)])
        else:
            # ถ้าไม่ใช่ช่วง ให้เพิ่ม interface โดยตรง
            interfaces_list.append(f"Ethernet{part}")

    return source_vlan, target_vlan, interfaces_list

# ฟังก์ชันสำหรับย้าย interfaces จาก VLAN ต้นทางไปยัง VLAN ปลายทาง
def move_interfaces_to_vlan(ip, source_vlan, target_vlan, interfaces):
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
        'secret': enable_password,
        'global_delay_factor': 2,
        'session_log': f"session_log_{ip}.txt"  # บันทึก log เพื่อตรวจสอบ prompt
    }

    try:
        # เชื่อมต่อกับ switch
        connection = ConnectHandler(**device)

        # เข้าสู่ enable mode โดยปรับ expect_string
        connection.enable()

        # เข้าสู่ configuration mode โดยใช้ read_timeout และ expect_string
        connection.config_mode()

        # ตั้งค่า interfaces ที่รับจากผู้ใช้ให้ย้ายไปยัง VLAN ใหม่
        for interface in interfaces:
            commands = [
                f"interface {interface}",
                "switchport mode access",
                f"switchport access vlan {target_vlan}"
            ]
            connection.send_config_set(commands, delay_factor=2, read_timeout=20)  # เพิ่ม read_timeout
            print(f"Moved {interface} on switch {ip} from VLAN {source_vlan} to VLAN {target_vlan}")

        # ออกจาก configuration mode และปิดการเชื่อมต่อ
        connection.exit_config_mode()
        connection.disconnect()
        print(f"Completed moving interfaces on switch {ip}")

    except Exception as e:
        print(f"Failed to connect or configure the device at {ip}: {e}")

# รับข้อมูลจากผู้ใช้
source_vlan, target_vlan, interfaces = get_user_input()

# สร้าง thread สำหรับแต่ละ IP
threads = [threading.Thread(target=move_interfaces_to_vlan, args=(ip, source_vlan, target_vlan, interfaces)) for ip in switch_ips]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
