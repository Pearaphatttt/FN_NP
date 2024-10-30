import threading
from netmiko import ConnectHandler

# กำหนดข้อมูลเข้าสู่ระบบและช่วง IP ของ switch
username = 'admin'
password = '123'
enable_password = '123'  # ใส่รหัสผ่าน enable ที่ตั้งค่าไว้

ip_start, ip_end = 114, 116
switch_ips = [f"90.90.126.{i}" for i in range(ip_start, ip_end + 1)]

# ฟังก์ชันสำหรับตั้งค่า VLAN บน switch แต่ละตัว
def configure_switch(ip):
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
        'secret': enable_password,  # ใช้รหัสผ่าน enable
    }

    try:
        # เชื่อมต่อกับ switch
        connection = ConnectHandler(**device)

        # เข้าสู่ enable mode
        connection.enable()

        # เข้าสู่ configuration mode และตั้งค่า VLANs
        connection.config_mode()

        for vlan_id in range(2, 10):
            connection.send_config_set([f"vlan {vlan_id}", f"name Python_VLAN_{vlan_id}"])

        # ออกจาก configuration mode และปิดการเชื่อมต่อ
        connection.exit_config_mode()
        connection.disconnect()
        print(f"Configured VLANs on switch {ip}")

    except Exception as e:
        print(f"Failed to connect or configure the device at {ip}: {e}")

# เริ่ม thread สำหรับแต่ละ IP
threads = [threading.Thread(target=configure_switch, args=(ip,)) for ip in switch_ips]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
