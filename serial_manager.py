import serial.tools.list_ports


class SerialManager:
    def __init__(self):
        self.serial_connection = None
        self.esp32_connected = False

    def find_esp32_port(self):
        esp32_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Silicon Labs' in p.manufacturer or
               'wch.cn' in p.manufacturer or 'USB-SERIAL CH340' in p.description
        ]
        if not esp32_ports:
            print("Warning: No ESP32 or FireBeetle found")
            return None
        if len(esp32_ports) > 1:
            print("Multiple ESP32s or FireBeetles found - using the first one")
        self.esp32_connected = True
        return esp32_ports[0]

    def open_connection(self, port):
        if port is None:
            return None
        self.serial_connection = serial.Serial(port, 115200)
        self.esp32_connected = True
        return self.serial_connection

    def write_to_serial(self, data):
        if not self.esp32_connected:
            print("No ESP32 or FireBeetle connection. Cannot write data.")
            return

        if self.serial_connection is None or not self.serial_connection.is_open:
            print("Serial connection is not open. Cannot write data.")
            return

        try:
            if isinstance(data, str):
                data_bytes = data.encode()
            else:
                data_bytes = data

            self.serial_connection.write(data_bytes)
        except serial.SerialException as e:
            print("Error writing to serial port:", e)
