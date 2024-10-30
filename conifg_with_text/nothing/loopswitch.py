from netmiko import ConnectHandler

username = 'cisco'
password = 'cisco'

for n in range(117, 120):
    IP = "192.168.1." + str(n)

    device = {
        'devicetype': 'cisco_ios',
        'ip': IP,
        'username': username,
        'password': password,
    }

    try:
        # Establish SSH connection
        connection = ConnectHandler(**device)
        connection.send_command("en")
        connection.send_command("123")

        # Enter configuration mode
        connection.send_command("conf t")

        # Configure VLANs
        for vlan_id in range(2, 10):
            connection.send_command(f"vlan {vlan_id}")
            connection.send_command(f"name Python_VLAN{vlan_id}")

        # Exit configuration mode
        connection.send_command("end")

        # Optionally, exit and print final output if needed
        output = connection.send_command("exit")
        print(f"Output from {IP}:\n{output}")

        # Close the SSH connection
        connection.disconnect()

    except Exception as e:
        print(f"Failed to connect to {IP}: {e}")