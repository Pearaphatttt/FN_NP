# นำเข้าฟังก์ชันที่จำเป็นจาก Flask และ Netmiko
from flask import Flask, render_template, request, redirect, url_for  # ใช้สำหรับจัดการเส้นทางเว็บและ HTML template
from netmiko import ConnectHandler  # ใช้เชื่อมต่อกับอุปกรณ์เครือข่าย

# เริ่มต้นแอป Flask
app = Flask(__name__)

# กำหนดตัวแปรสำหรับการเชื่อมต่ออุปกรณ์เครือข่าย (เก็บ ConnectHandler)
net_connect = None

##################################################################################################
# สร้างเส้นทาง (route) หน้าแรก ใช้วิธี GET แสดงหน้า login ###*********** -------->เลือกใช้ function นี้ถ้ามีให้ทำหน้า login<----------------  ***************
# @app.route('/', methods=['GET'])
# def index():
#     return render_template('login.html')  # แสดงผลหน้า login.html ให้ผู้ใช้กรอกข้อมูล

# # สร้างเส้นทางเชื่อมต่ออุปกรณ์ ใช้วิธี POST (รับข้อมูลจากฟอร์ม)
# @app.route('/connect', methods=['POST'])  
# def connect():
#     global net_connect  # กำหนด net_connect เป็นตัวแปร global
#     ip = request.form['ip']  # ดึงข้อมูล IP จากฟอร์ม
#     username = request.form['username']  # ดึงข้อมูล Username จากฟอร์ม
#     password = request.form['password']  # ดึงข้อมูล Password จากฟอร์ม

#     # สร้างข้อมูลการตั้งค่าอุปกรณ์เครือข่าย (router)
#     router = {
#         'device_type': 'cisco_ios',  # ระบุประเภทของอุปกรณ์ (ที่นี่เป็น Cisco iOS)
#         'ip': ip,  # กำหนด IP Address ที่ได้จากฟอร์ม
#         'username': username,  # กำหนดชื่อผู้ใช้ที่ได้จากฟอร์ม
#         'password': password,  # กำหนดรหัสผ่านที่ได้จากฟอร์ม
#         'secret': password,  # ตั้งค่า secret ให้เหมือนกับ password
#     }

#     try:
#         # เชื่อมต่ออุปกรณ์ด้วย ConnectHandler และเข้าโหมด enable
#         net_connect = ConnectHandler(**router)
#         net_connect.enable()  

#         # ดึงข้อมูล prompt เพื่อแสดงผลบนหน้าเว็บ
#         prompt = net_connect.find_prompt()
#         return render_template('homepage.html', output="", prompt=prompt)  # แสดงหน้า homepage
#     except Exception as e:
#         # แสดงข้อความแจ้งเตือนเมื่อเกิดข้อผิดพลาด
#         return f'<h1>ว้ายยย login ไม่ได้</h1><p>Error: {str(e)}</p>'
####################################################################################################################

############################################ ---- เชื่อมต่ออุปกรณ์ ---- ###########################################
@app.route('/', methods=['GET'])
def homepage():
    # กำหนด IP, Username และ Password ในโค้ด
    ip = "192.168.136.130"
    username = "admin"
    password = "123"

    # สร้างข้อมูลการตั้งค่าอุปกรณ์เครือข่าย
    router = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
        'secret': password,  
    }

    try:
        global net_connect  # ใช้ตัวแปร net_connect จาก global
        net_connect = ConnectHandler(**router)  # สร้างการเชื่อมต่อ
        net_connect.enable()  # เข้าโหมด enable

        prompt = net_connect.find_prompt()  # ดึงข้อมูล prompt
        return render_template('homepage.html', output="", prompt=prompt)  # แสดงหน้า homepage
    except Exception as e:
        # แสดงข้อผิดพลาดเมื่อเชื่อมต่อไม่ได้
        return f'<h1>ว้ายยย login ไม่ได้</h1><p>Error: {str(e)}</p>'
##################################################################################################################

####################################---- คำสั่ง SHOW ----##########################################
@app.route('/show_run', methods=['POST'])
def show_run():

    global net_connect  # ใช้ตัวแปร net_connect จาก global
    if not net_connect:  # ตรวจสอบว่ามีการเชื่อมต่อแล้วหรือไม่
        return '<h1>เข้าไม่ได้หรอกไอโง่เขียนโค้ดก็ผิด</h1>'
    
    try:
        output = net_connect.send_command('show run')  # ส่งคำสั่ง 'show run' ไปยังอุปกรณ์
        return render_template('Homepage.html', output=output)  # แสดงผลลัพธ์บนหน้า Homepage
    except Exception as e:
        return f'<h1>ไม่ไหร่จะเขียนโค้ดถูก</h1>'

@app.route('/show_ip_interface', methods=['POST'])
def show_ip_interface():

    global net_connect  # ใช้ตัวแปร net_connect จาก global
    if not net_connect:  # ตรวจสอบว่ามีการเชื่อมต่อแล้วหรือไม่
        return '<h1>เข้าไม่ได้หรอกไอโง่เขียนโค้ดก็ผิด</h1>'
    
    try:
        output = net_connect.send_command('show ip interface brief')  # ส่งคำสั่ง 'show ip interface brief'
        prompt = net_connect.find_prompt()  # ดึงข้อมูล prompt
        return render_template('Homepage.html', output=output, prompt=prompt)  # แสดงผลลัพธ์และ prompt บนหน้า Homepage
    except Exception as e:
        return f'<h1>ไม่ไหร่จะเขียนโค้ดถูก</h1>'

@app.route('/show_iproute', methods=['POST'])
def show_iproute():

    global net_connect
    if not net_connect:
        return '<h1>เข้าไม่ได้หรอกไอโง่เขียนโค้ดก็ผิด</h1>'
    
    try:
        output = net_connect.send_command('show ip route')  # ส่งคำสั่ง 'show ip route'
        prompt = net_connect.find_prompt()
        return render_template('Homepage.html', output=output, prompt=prompt)
    except Exception as e:
        return f'<h1>ไม่ไหร่จะเขียนโค้ดถูก</h1>'
###########################################################################################


########################เพิ่ม IP Interface ของ Router ######################################
@app.route('/config_interface_router', methods=['POST'])
def config_interface_router():

    global net_connect
    if not net_connect:
        return '<h1>Error</h1>'

    interface = request.form['interface']  # รับข้อมูล interface จากฟอร์ม
    ip_address = request.form['ip_address']  # รับข้อมูล IP address จากฟอร์ม
    subnet_mask = request.form['subnet_mask']  # รับข้อมูล subnet mask จากฟอร์ม

    # กำหนดคำสั่งสำหรับตั้งค่า IP ให้ interface
    commands = [
        f"interface {interface}",
        "no ip address",  # ลบ IP ที่ตั้งค่าไว้ก่อนหน้า
        f"ip address {ip_address} {subnet_mask}",
        "no sh",  # เปิดการใช้งาน interface
        "exit",
    ]

    try:
        net_connect.send_config_set(commands)  # ส่งคำสั่งตั้งค่า IP ไปยังอุปกรณ์
        output = net_connect.send_command('sh ip int br')  # แสดงผลการตั้งค่า
        return render_template('homepage.html', outpt=output)
    except Exception as e:
        return f'<h1>Error Applying Router Interface Config</h1><p>{str(e)}</p>'
#########################################################################################



################################## ลบ IP Interface #####################################
@app.route('/remove_ip_interface', methods=['POST'])
def remove_ip_interface():

    global net_connect
    if not net_connect:
        return '<h1>Error</h1>'

    interface = request.form['interface']  # รับข้อมูล interface จากฟอร์ม

    # กำหนดคำสั่งสำหรับลบ IP จาก interface
    commands = [
        f"interface {interface}",
        "no ip address",  # ลบ IP address
        "exit",
    ]

    try:
        output = net_connect.send_config_set(commands)
        prompt = net_connect.find_prompt()
        return render_template('homepage.html', outpt=output, prompt=prompt)
    except Exception as e:
        return f'<h1>Error Remove IP Interface </h1><p>{str(e)}</p>'
################################################################################################


################################### ปิดใช้งาน interface #########################################
@app.route('/shutdown_interface', methods=['POST'])
def shutdown_interface():

    global net_connect
    if not net_connect:
        return '<h1>Error</h1>'

    interface = request.form['interface']  # รับข้อมูล interface จากฟอร์ม

    # กำหนดคำสั่งปิดใช้งาน interface
    commands = [
        f"interface {interface}",
        "shutdown",  # ปิดการใช้งาน interface
        "exit",
    ]

    try:
        output = net_connect.send_config_set(commands)
        prompt = net_connect.find_prompt()
        return render_template('homepage.html', outpt=output, prompt=prompt)
    except Exception as e:
        return f'<h1>Error Shut Down Interface </h1><p>{str(e)}</p>'
###################################################################################################


################################### เปิดใช้งาน interface #####################################################
@app.route('/noshutdown_interface', methods=['POST'])
def noshutdown_interface():

    global net_connect
    if not net_connect:
        return '<h1>Error</h1>'

    interface = request.form['interface']  # รับข้อมูล interface จากฟอร์ม

    # กำหนดคำสั่งเปิดใช้งาน interface
    commands = [
        f"interface {interface}",
        "no shutdown",  # เปิดใช้งาน interface
        "exit",
    ]

    try:
        output = net_connect.send_config_set(commands)
        prompt = net_connect.find_prompt()
        return render_template('homepage.html', outpt=output, prompt=prompt)
    except Exception as e:
        return f'<h1>Error Shut Down Interface </h1><p>{str(e)}</p>'
###########################################################################################################


########################################### ตั้งค่า IP Route ######################################################
@app.route('/ip_route', methods=['POST'])
def ip_route():

    global net_connect
    if not net_connect:
        return '<h1>Error</h1>'

    network = request.form['network']  # รับข้อมูล network จากฟอร์ม
    subnet_mask = request.form['subnet_mask']  # รับข้อมูล subnet mask จากฟอร์ม
    next_hop = request.form['next_hop']  # รับข้อมูล next hop จากฟอร์ม

    # กำหนดคำสั่งตั้งค่า IP route
    commands = [
        f"ip route {network} {subnet_mask} {next_hop}"
    ]

    try:
        output = net_connect.send_config_set(commands)
        return render_template('homepage.html', outpt=output)
    except Exception as e:
        return f'<h1>Error IP router</h1><p>{str(e)}</p>'
#############################################################################################################

# รันแอปในโหมด debug สำหรับการทดสอบ
if __name__ == '__main__':
    app.run(debug=True)
