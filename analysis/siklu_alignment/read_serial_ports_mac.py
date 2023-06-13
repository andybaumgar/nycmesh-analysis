import serial.tools.list_ports

# Get a list of available ports
ports = serial.tools.list_ports.comports()

# Iterate over the ports and print their details
for port in ports:
    print(f"Port: {port.device}, Description: {port.description}")
