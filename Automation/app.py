from flask import Flask, render_template, request, redirect, url_for
from netmiko import ConnectHandler
import time
import threading

app = Flask(__name__)

# ตัวแปร global สำหรับเก็บการเชื่อมต่อ SSH
net_connect = None

@app.route('/', methods=['GET'])
def index():
    """
    เส้นทางหลักของแอปพลิเคชัน แสดงหน้า index.html ซึ่งเป็นหน้าแรก
    """
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    """
    ฟังก์ชันสำหรับเชื่อมต่อกับอุปกรณ์เครือข่ายผ่าน SSH
    รับข้อมูล IP, username และ password จากแบบฟอร์ม
    """
    global net_connect
    ip = request.form['ip']
    username = request.form['username']
    password = request.form['password']

    # สร้างพารามิเตอร์การเชื่อมต่อ
    router = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
        'secret': password,  # ใช้สำหรับเข้าสู่โหมด enable
    }

    try:
        # เชื่อมต่อกับอุปกรณ์
        net_connect = ConnectHandler(**router)
        net_connect.enable()  # เข้าสู่โหมด enable

        # ดึง hostname จากอุปกรณ์
        hostname = get_hostname()
        prompt = net_connect.find_prompt()

        # แสดงหน้า command_center.html พร้อมส่งค่า hostname และ prompt
        return render_template('command_center.html', output="", prompt=prompt, hostname=hostname)
    except Exception as e:
        # แสดงข้อความ error ถ้าเชื่อมต่อไม่สำเร็จ
        return f'<h1>Error Connecting to Device: {str(e)}</h1>'

@app.route('/run_command', methods=['POST'])
def run_command():
    """
    ฟังก์ชันสำหรับรันคำสั่งที่ผู้ใช้กรอกผ่านเว็บอินเทอร์เฟซ
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    command = request.form['command']
    try:
        # ส่งคำสั่งไปยังอุปกรณ์และรับผลลัพธ์
        output = net_connect.send_command(command)
        prompt = net_connect.find_prompt()
        # แสดงผลลัพธ์ในหน้า command_center.html
        return render_template('command_center.html', output=output, prompt=prompt)
    except Exception as e:
        return f'<h1>Error Running Command</h1><p>{str(e)}</p>'

@app.route('/show_version', methods=['POST'])
def show_version():
    """
    ฟังก์ชันสำหรับแสดงข้อมูลเวอร์ชันของอุปกรณ์ (show version)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1><p>Please connect first.</p>'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")  # แสดง hostname ใน console

        # ส่งคำสั่ง 'show version' และรับผลลัพธ์
        output = net_connect.send_command('show version')
        prompt = net_connect.find_prompt()
        # แสดงผลลัพธ์ในหน้า show_commands.html
        return render_template('show_commands.html', output=output, prompt=prompt, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Version</h1><p>{str(e)}</p>'

# ฟังก์ชันอื่นๆ ที่มีลักษณะคล้ายกันสำหรับรันคำสั่ง 'show' ต่างๆ

@app.route('/show_running_config', methods=['POST'])
def show_running_config():
    """
    ฟังก์ชันสำหรับแสดงการตั้งค่าปัจจุบันของอุปกรณ์ (show running-config)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        output = net_connect.send_command('show running-config')
        prompt = net_connect.find_prompt()
        return render_template('show_commands.html', output=output, prompt=prompt, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Running Config</h1><p>{str(e)}</p>'

@app.route('/show_startup_config', methods=['POST'])
def show_startup_config():
    """
    ฟังก์ชันสำหรับแสดงการตั้งค่าเมื่อเริ่มต้นของอุปกรณ์ (show startup-config)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        output = net_connect.send_command('show startup-config')
        prompt = net_connect.find_prompt()
        return render_template('show_commands.html', output=output, prompt=prompt, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Startup Config</h1><p>{str(e)}</p>'

@app.route('/show_ip_interface_brief', methods=['POST'])
def show_ip_interface_brief():
    """
    ฟังก์ชันสำหรับแสดงข้อมูลสรุปของอินเทอร์เฟซ IP (show ip interface brief)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        output = net_connect.send_command('show ip interface brief')
        prompt = net_connect.find_prompt()
        return render_template('show_commands.html', output=output, prompt=prompt, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing IP Interface Brief</h1><p>{str(e)}</p>'

@app.route('/show_interfaces', methods=['POST'])
def show_interfaces():
    """
    ฟังก์ชันสำหรับแสดงรายละเอียดของอินเทอร์เฟซทั้งหมด (show interfaces)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        output = net_connect.send_command('show interfaces')
        prompt = net_connect.find_prompt()
        return render_template('show_commands.html', output=output, prompt=prompt, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Interfaces</h1><p>{str(e)}</p>'

@app.route('/show_ip_route', methods=['POST'])
def show_ip_route():
    """
    ฟังก์ชันสำหรับแสดงตารางเส้นทาง IP (show ip route)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        output = net_connect.send_command('show ip route')
        prompt = net_connect.find_prompt()
        return render_template('show_commands.html', output=output, prompt=prompt, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing IP Route</h1><p>{str(e)}</p>'

# ฟังก์ชันเพิ่มเติมสำหรับคำสั่ง 'show' อื่นๆ เช่น show_arp, show_protocols, show_clock, etc.

@app.route('/show_arp', methods=['POST'])
def show_arp():
    """
    ฟังก์ชันสำหรับแสดงตาราง ARP (show arp)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        output = net_connect.send_command('show arp')
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('show_commands.html', output=output, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing ARP</h1><p>{str(e)}</p>'

@app.route('/show_protocols', methods=['POST'])
def show_protocols():
    """
    ฟังก์ชันสำหรับแสดงข้อมูลโปรโตคอลที่ใช้งานอยู่ (show protocols)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        output = net_connect.send_command('show protocols')
        return render_template('show_commands.html', output=output, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Protocols</h1><p>{str(e)}</p>'

@app.route('/show_clock', methods=['POST'])
def show_clock():
    """
    ฟังก์ชันสำหรับแสดงเวลาปัจจุบันของอุปกรณ์ (show clock)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        output = net_connect.send_command('show clock')
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('show_commands.html', output=output, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Clock</h1><p>{str(e)}</p>'

@app.route('/show_users', methods=['POST'])
def show_users():
    """
    ฟังก์ชันสำหรับแสดงผู้ใช้ที่กำลังเชื่อมต่อกับอุปกรณ์ (show users)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        output = net_connect.send_command('show users')
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('show_commands.html', output=output, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing Users</h1><p>{str(e)}</p>'

@app.route('/show_history', methods=['POST'])
def show_history():
    """
    ฟังก์ชันสำหรับแสดงประวัติคำสั่งที่รันก่อนหน้า (show history)
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        output = net_connect.send_command('show history')
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('show_commands.html', output=output, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing History</h1><p>{str(e)}</p>'

@app.route('/show_vlan_brief', methods=['POST'])
def show_vlan_brief():
    """
    ฟังก์ชันสำหรับแสดงข้อมูล VLAN สรุป (show vlan brief) สำหรับ Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    # ตรวจสอบว่าเป็น Switch หรือไม่
    version_output = net_connect.send_command('show version')
    if 'vios_l2' in version_output:
        # ถ้าเป็น Switch แสดงข้อมูล VLAN
        output = net_connect.send_command('show vlan brief')
    else:
        # ถ้าไม่ใช่ แสดงข้อความแจ้งเตือน
        output = 'You are not connected to a Switch. VLAN information is not available.'

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('show_commands.html', output=output, hostname=hostname)
    except Exception as e:
        return f'<h1>Error Showing VLAN Brief</h1><p>{str(e)}</p>'

# ฟังก์ชันสำหรับจัดการการกลับไปยังหน้า command_center

@app.route('/back', methods=['POST'])
def back():
    return redirect(url_for('command_center'))

@app.route('/command_center')
def command_center():
    """
    ฟังก์ชันสำหรับแสดงหน้า command_center.html
    """
    global net_connect
    if not net_connect:
        return redirect(url_for('index'))

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('command_center.html', output="", hostname=hostname)
    except Exception as e:
        print(f"Error: {e}")
        return '<h1>Error</h1>'

# ฟังก์ชันสำหรับแสดงหน้า show_commands.html

@app.route('/show_commands', methods=['GET'])
def show_commands():
    """
    ฟังก์ชันสำหรับแสดงหน้า show_commands.html
    """
    global net_connect
    if not net_connect:
        return redirect(url_for('index'))

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('show_commands.html', output="", hostname=hostname)
    except Exception as e:
        print(f"Error: {e}")
        return '<h1>Error</h1>'

@app.route('/all_config', methods=['GET'])
def all_config():
    """
    ฟังก์ชันสำหรับแสดงหน้า all_config.html
    """
    global net_connect
    if not net_connect:
        return redirect(url_for('index'))

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('all_config.html', output="", hostname=hostname)
    except Exception as e:
        print(f"Error: {e}")
        return '<h1>Error</h1>'

# ฟังก์ชันสำหรับจัดการคำสั่ง erase และ reload อุปกรณ์

def erase_and_reload_router():
    """
    ฟังก์ชันที่รันใน background สำหรับลบการตั้งค่าและรีโหลดอุปกรณ์
    """
    global net_connect
    try:
        # ส่งคำสั่ง 'write erase' เพื่อลบการตั้งค่า
        output = net_connect.send_command_timing('write erase')
        time.sleep(2)

        # ตรวจสอบว่าต้องยืนยันการลบหรือไม่
        if 'Erasing the nvram filesystem' in output or 'Continue? [confirm]' in output:
            output += net_connect.send_command_timing('\n')
            time.sleep(2)

        # ส่งคำสั่ง 'reload' เพื่อรีโหลดอุปกรณ์
        reload_output = net_connect.send_command_timing('reload')
        time.sleep(2)

        # จัดการกับข้อความยืนยันต่างๆ
        if 'System configuration has been modified. Save? [yes/no]:' in reload_output:
            reload_output += net_connect.send_command_timing('no\n')
            time.sleep(2)

        if 'Proceed with reload' in reload_output or 'confirm' in reload_output:
            reload_output += net_connect.send_command_timing('y\n')
            time.sleep(2)
            reload_output += "\nConfiguration erased and router is reloading...\n"
        else:
            reload_output += "\nReload command failed due to restrictions on Telnet/SSH sessions.\n"
            reload_output += "Please manually reload the router using the console connection."

        print(output + reload_output)  # สำหรับ debugging
    except Exception as e:
        print(f"Error during erase/reload: {str(e)}")
    finally:
        net_connect.disconnect()
        net_connect = None

@app.route('/erase_router', methods=['POST'])
def erase_router():
    """
    ฟังก์ชันสำหรับเรียกใช้การลบการตั้งค่าและรีโหลดอุปกรณ์
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    # รันฟังก์ชัน erase_and_reload_router ใน thread แยก
    threading.Thread(target=erase_and_reload_router).start()
    return render_template('all_config.html', output="Erase command sent. Router is reloading...")

# ฟังก์ชันสำหรับจัดการการตั้งค่าอินเทอร์เฟซของ Router และ Switch

@app.route('/apply_router_interface_config', methods=['POST'])
def apply_router_interface_config():
    """
    ฟังก์ชันสำหรับตั้งค่า IP Address ให้กับอินเทอร์เฟซของ Router
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    interface = request.form['interface']
    ip_address = request.form['ip_address']
    subnet_mask = request.form['subnet_mask']

    commands = [
        f"interface {interface}",
        "no ip address",  # ลบ IP เดิม
        f"ip address {ip_address} {subnet_mask}",
        "no shutdown",
        "exit",
    ]
    try:
        interfaces = get_interfaces()
        hostname = get_hostname()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        prompt = net_connect.find_prompt()
        return render_template('conf_router.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces)
    except Exception as e:
        return f'<h1>Error Applying Router Interface Config</h1><p>{str(e)}</p>'

@app.route('/apply_switch_interface_config', methods=['POST'])
def apply_switch_interface_config():
    """
    ฟังก์ชันสำหรับตั้งค่า IP Address ให้กับอินเทอร์เฟซของ Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    interface = request.form['interface']
    ip_address = request.form['ip_address']
    subnet_mask = request.form['subnet_mask']

    commands = [
        f"interface {interface}",
        "no switchport",  # เปลี่ยนอินเทอร์เฟซเป็น Layer 3
        f"ip address {ip_address} {subnet_mask}",
        "no shutdown",
        "exit"
    ]
    try:
        interfaces = get_interfaces()
        hostname = get_hostname()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces)
    except Exception as e:
        return f'<h1>Error Applying Switch Interface Config</h1><p>{str(e)}</p>'

@app.route('/remove_router_ip_interface', methods=['POST'])
def remove_router_ip_interface():
    """
    ฟังก์ชันสำหรับลบ IP Address ออกจากอินเทอร์เฟซของ Router
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    interface = request.form['interface']

    commands = [
        f"interface {interface}",
        "no ip address",  # ลบ IP address
        "exit"
    ]
    try:
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        prompt = net_connect.find_prompt()
        return render_template('conf_router.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces)
    except Exception as e:
        return f'<h1>Error Removing Router IP Address</h1><p>{str(e)}</p>'

@app.route('/remove_switch_ip_interface', methods=['POST'])
def remove_switch_ip_interface():
    """
    ฟังก์ชันสำหรับลบ IP Address ออกจากอินเทอร์เฟซของ Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    interface = request.form['interface']

    commands = [
        f"interface {interface}",
        "no ip address",  # ลบ IP address
        "exit"
    ]
    try:
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        output += "\n" + net_connect.send_command(f"show ip interface brief | include {interface}")
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces)
    except Exception as e:
        return f'<h1>Error Removing Switch IP Address</h1><p>{str(e)}</p>'

# ฟังก์ชันสำหรับการจัดการ IP Route

@app.route('/ip_route')
def ip_route():
    """
    ฟังก์ชันสำหรับแสดงหน้า ip_route.html สำหรับการตั้งค่า Static Route
    """
    global net_connect
    if not net_connect:
        return redirect(url_for('index'))

    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('ip_route.html', hostname=hostname)
    except Exception as e:
        print(f"Error: {e}")
        return '<h1>Error</h1>'

@app.route('/submit_ip_route', methods=['POST'])
def submit_ip_route():
    """
    ฟังก์ชันสำหรับเพิ่ม Static Route
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    network = request.form['network']
    subnet_mask = request.form['subnet_mask']
    nexthop = request.form['nexthop']

    # สร้างคำสั่งสำหรับเพิ่ม route
    route_command = f"ip route {network} {subnet_mask} {nexthop}"

    try:
        # เข้าสู่โหมด configuration
        net_connect.config_mode()

        # ส่งคำสั่งไปยังอุปกรณ์
        output = net_connect.send_config_set(route_command)
        output = f"Route added: {network}/{subnet_mask} via {nexthop}\n{output}"

        hostname = get_hostname()
        print(f"Hostname: {hostname}")
        return render_template('ip_route.html', output=output, hostname=hostname)
    except Exception as e:
        output = f"Failed to add route: {str(e)}"
        return render_template('ip_route.html', output=output)

# ฟังก์ชันสำหรับการตั้งค่า Router และ Switch

@app.route('/conf_router', methods=['GET'])
def conf_router():
    """
    ฟังก์ชันสำหรับแสดงหน้า conf_router.html สำหรับตั้งค่า Router
    """
    global net_connect
    if not net_connect:
        return redirect(url_for('index'))

    try:
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")
        return render_template('conf_router.html', hostname=hostname, interfaces=interfaces)
    except Exception as e:
        print(f"Error: {e}")
        return '<h1>Error</h1>'

@app.route('/conf_switch', methods=['GET'])
def conf_switch():
    """
    ฟังก์ชันสำหรับแสดงหน้า conf_switch.html สำหรับตั้งค่า Switch
    """
    global net_connect
    if not net_connect:
        return redirect(url_for('index'))

    try:
        vlan_ids = get_vlan_ids()
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")
        return render_template('conf_switch.html', hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        print(f"Error: {e}")
        return '<h1>Error</h1>'

# ฟังก์ชันสำหรับจัดการ VLAN บน Switch

@app.route('/add_vlan', methods=['POST'])
def add_vlan():
    """
    ฟังก์ชันสำหรับเพิ่ม VLAN บน Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    vlan_id = request.form['vlan_id']
    vlan_name = request.form['vlan_name']
    interface = request.form['interface']

    commands = [
        f"vlan {vlan_id}",
        f"name {vlan_name}",
        "exit",
        f"interface {interface}",
        f"switchport access vlan {vlan_id}",
        "exit"
    ]
    try:
        vlan_ids = get_vlan_ids()
        interfaces = get_interfaces()
        hostname = get_hostname()
        print(f"Hostname: {hostname}")

        net_connect.send_config_set(commands)
        output = net_connect.send_command(f"show vlan brief | include {vlan_id}")
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        return f'<h1>Error Adding VLAN</h1><p>{str(e)}</p>'

@app.route('/remove_vlan', methods=['POST'])
def remove_vlan():
    """
    ฟังก์ชันสำหรับลบ VLAN บน Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    vlan_id = request.form['vlan_id']

    commands = [
        f"no vlan {vlan_id}"
    ]
    try:
        vlan_ids = get_vlan_ids()
        interfaces = get_interfaces()
        hostname = get_hostname()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        output += net_connect.send_command("show vlan brief")
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        return f'<h1>Error Removing VLAN</h1><p>{str(e)}</p>'

@app.route('/add_ip_vlan', methods=['POST'])
def add_ip_vlan():
    """
    ฟังก์ชันสำหรับเพิ่ม IP Address ให้กับ VLAN Interface บน Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    vlan_id = request.form['vlan_id']
    ip_address = request.form['ip_address']
    subnet_mask = request.form['subnet_mask']

    commands = [
        f"interface vlan {vlan_id}",
        f"ip address {ip_address} {subnet_mask}",
        "no shutdown",
        "exit"
    ]
    try:
        vlan_ids = get_vlan_ids()
        interfaces = get_interfaces()
        hostname = get_hostname()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        output += net_connect.send_command(f"show ip interface brief | include Vlan{vlan_id}")
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        return f'<h1>Error Adding IP to VLAN</h1><p>{str(e)}</p>'

@app.route('/add_port_to_vlan', methods=['POST'])
def add_port_to_vlan():
    """
    ฟังก์ชันสำหรับเพิ่มพอร์ตเข้าไปใน VLAN บน Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'

    interface = request.form['interface']
    vlan_id = request.form['vlan_id']

    commands = [
        f"interface {interface}",
        f"switchport access vlan {vlan_id}",
        "no shutdown",
        "exit"
    ]
    try:
        vlan_ids = get_vlan_ids()
        interfaces = get_interfaces()
        hostname = get_hostname()
        print(f"Hostname: {hostname}")

        output = net_connect.send_config_set(commands)
        output += net_connect.send_command(f"show vlan brief | include {vlan_id}")
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        return f'<h1>Error Adding Port to VLAN</h1><p>{str(e)}</p>'

# ฟังก์ชันสำหรับแสดง VLANs ในหน้า conf_switch

@app.route('/show_vlans', methods=['POST'])
def show_vlans():
    """
    ฟังก์ชันสำหรับแสดง VLAN ทั้งหมดบน Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        vlan_ids = get_vlan_ids()
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")

        output = net_connect.send_command('show vlan brief')
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        return f'<h1>Error Showing VLANs</h1><p>{str(e)}</p>'

# ฟังก์ชันสำหรับแสดง interfaces ในหน้า conf_switch

@app.route('/show_interfaces_switch', methods=['POST'])
def show_interfaces_switch():
    """
    ฟังก์ชันสำหรับแสดงอินเทอร์เฟซบน Switch
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        vlan_ids = get_vlan_ids()
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")

        output = net_connect.send_command('show ip interface brief')
        prompt = net_connect.find_prompt()
        return render_template('conf_switch.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces, vlan_ids=vlan_ids)
    except Exception as e:
        return f'<h1>Error Showing Interfaces</h1><p>{str(e)}</p>'

@app.route('/show_interfaces_router', methods=['POST'])
def show_interfaces_router():
    """
    ฟังก์ชันสำหรับแสดงอินเทอร์เฟซบน Router
    """
    global net_connect
    if not net_connect:
        return '<h1>Not connected</h1>'
    try:
        hostname = get_hostname()
        interfaces = get_interfaces()
        print(f"Hostname: {hostname}")

        output = net_connect.send_command('show ip interface brief')
        prompt = net_connect.find_prompt()
        return render_template('conf_router.html', output=output, prompt=prompt, hostname=hostname, interfaces=interfaces)
    except Exception as e:
        return f'<h1>Error Showing Interfaces</h1><p>{str(e)}</p>'

def get_hostname():
    """
    ฟังก์ชันสำหรับดึง hostname ของอุปกรณ์เครือข่าย
    """
    global net_connect
    try:
        # ส่งคำสั่ง 'show running-config' เพื่อดึงข้อมูลการตั้งค่าปัจจุบัน
        output = net_connect.send_command("show running-config")
        print("Output of show running-config:")
        print(output)  # แสดงผลลัพธ์ใน console

        lines = output.splitlines()
        # หา line ที่มีคำว่า 'hostname' เพื่อดึงชื่อ hostname
        hostname_line = next((line for line in lines if line.startswith("hostname")), None)
        hostname = hostname_line.split()[-1] if hostname_line else "Unknown"
        return hostname
    except Exception as e:
        print(f"Error getting hostname: {e}")
        return "Unknown"


# ฟังก์ชันสำหรับดึงข้อมูลอินเทอร์เฟซและ VLAN

def get_interfaces():
    """
    ฟังก์ชันสำหรับดึงรายการอินเทอร์เฟซจากอุปกรณ์
    """
    global net_connect
    try:
        output = net_connect.send_command("show ip interface brief")
        lines = output.splitlines()
        interfaces = []
        for line in lines[1:]:  # ข้ามหัวข้อ
            parts = line.split()
            if len(parts) > 0:
                interface = parts[0]
                interfaces.append(interface)
        return interfaces
    except Exception as e:
        print(f"Error getting interfaces: {e}")
        return []

def get_vlan_ids():
    """
    ฟังก์ชันสำหรับดึงรายการ VLAN IDs จากอุปกรณ์
    """
    try:
        output = net_connect.send_command("show vlan brief")
        vlan_lines = output.splitlines()
        vlan_ids = []
        for line in vlan_lines:
            if line and "VLAN" not in line:  # ข้ามบรรทัดที่มีคำว่า "VLAN"
                parts = line.split()
                if len(parts) > 0:
                    vlan_ids.append(parts[0])  # เก็บ VLAN ID
        return vlan_ids
    except Exception as e:
        print(f"Error retrieving VLAN IDs: {e}")
        return []

# ฟังก์ชันหลักในการรันแอปพลิเคชัน

if __name__ == '__main__':
    app.run(debug=True)
