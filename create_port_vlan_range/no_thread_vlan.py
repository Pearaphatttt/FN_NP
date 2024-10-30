from netmiko import ConnectHandler  # นำเข้า ConnectHandler จาก Netmiko สำหรับการเชื่อมต่อกับอุปกรณ์เครือข่าย

# กำหนดข้อมูลเข้าสู่ระบบและช่วง IP ของ switch
username = 'admin'  # ชื่อผู้ใช้สำหรับเข้าสู่ระบบ switch
password = '123'  # รหัสผ่านของผู้ใช้
enable_password = '123'  # รหัสผ่าน enable เพื่อเข้าสู่โหมด enable บน switch

switch_ips = ["90.90.126.114"]  # รายการ IP ของ switch ที่จะเชื่อมต่อและตั้งค่า

# ฟังก์ชันสำหรับตั้งค่า VLAN บน switch แต่ละตัว
def configure_switch(ip):
    device = {
        'device_type': 'cisco_ios',  # ระบุประเภทอุปกรณ์เป็น Cisco IOS
        'ip': ip,  # กำหนด IP ของ switch
        'username': username,  # ระบุชื่อผู้ใช้
        'password': password,  # ระบุรหัสผ่านของผู้ใช้
        'secret': enable_password,  # ใช้รหัสผ่าน enable
    }

    try:
        # เชื่อมต่อกับ switch
        connection = ConnectHandler(**device)
        
        # เข้าสู่ enable mode
        connection.enable()

        # เข้าสู่ configuration mode และตั้งค่า VLANs
        connection.config_mode()

        # สร้างและตั้งค่า VLAN 138 และตั้งค่า IP ให้กับ interface VLAN
        vlan_commands = [
            "vlan 140",
            "name Python_VLAN_140",
            "interface vlan 140",
            "ip address 10.10.140.1 255.255.255.0",
            "no shutdown",
            "exit"
        ]
        connection.send_config_set(vlan_commands)  # ส่งชุดคำสั่ง VLAN ไปยัง switch
        
        # ออกจาก configuration mode และปิดการเชื่อมต่อ
        connection.exit_config_mode()
        connection.disconnect()
        print(f"Configured VLANs on switch {ip} successfully.")

    except Exception as e:
        print(f"Failed to connect or configure the device at {ip}: {e}")  # แจ้งเตือนเมื่อเกิดข้อผิดพลาด

# เรียกใช้ฟังก์ชัน configure_switch กับทุก IP ใน switch_ips
for ip in switch_ips:
    configure_switch(ip)
