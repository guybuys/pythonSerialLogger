import serial_manager
import threading
import datetime
import sys


def create_log_file():
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M-%S_log.txt")
    return open(filename, 'a')


class SerialLogger:
    def __init__(self):
        self.serial_manager = serial_manager.SerialManager()
        self.log_file = None
        self.running = True

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} {message}\n"
        if self.log_file:
            self.log_file.write(log_message)
            self.log_file.flush()
        print(log_message, end='')

    def read_from_serial(self):
        while self.running:
            if self.serial_manager.serial_connection and self.serial_manager.serial_connection.in_waiting > 0:
                try:
                    data = self.serial_manager.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    self.log(f"=> {data}")
                except UnicodeDecodeError as e:
                    self.log(f"Error decoding data: {e}")

    def read_from_keyboard(self):
        while self.running:
            try:
                user_input = sys.stdin.read().strip()
                with self.lock:
                    self.serial_manager.write_to_serial(user_input.encode('utf-8', errors='ignore'))
                self.log(f"<= {user_input}")
            except UnicodeDecodeError as e:
                self.log(f"Error decoding input: {e}")

    def start(self):
        port = self.serial_manager.find_esp32_port()
        if port is None:
            print("No ESP32 connected. Exiting.")
            return

        self.serial_manager.open_connection(port)
        self.log_file = create_log_file()

        serial_thread = threading.Thread(target=self.read_from_serial)
        keyboard_thread = threading.Thread(target=self.read_from_keyboard)

        serial_thread.start()
        keyboard_thread.start()

        serial_thread.join()
        keyboard_thread.join()

    def stop(self):
        self.running = False
        if self.serial_manager.serial_connection:
            self.serial_manager.serial_connection.close()
        if self.log_file:
            self.log_file.close()


if __name__ == '__main__':
    logger = SerialLogger()
    try:
        logger.start()
    except KeyboardInterrupt:
        logger.stop()
