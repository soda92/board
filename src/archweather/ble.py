from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService


class BLEManager:
    def __init__(self, name="ArchWeather"):
        self.ble = BLERadio()
        self.ble.name = name
        self.uart = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart)

    def start_advertising(self):
        self.ble.start_advertising(self.advertisement)

    def stop_advertising(self):
        self.ble.stop_advertising()

    @property
    def connected(self):
        return self.ble.connected

    def send_data(self, temp, humidity):
        if self.connected:
            try:
                payload = f"{temp:.2f},{humidity:.2f}\n"
                self.uart.write(payload.encode("utf-8"))
                print(f"Sent: {payload.strip()}")
            except Exception as e:
                print(f"Error sending data: {e}")

    def read_command(self):
        if self.connected and self.uart.in_waiting > 0:
            try:
                data = self.uart.read(self.uart.in_waiting)
                if data:
                    # Decode and strip whitespace/newlines
                    return data.decode("utf-8").strip().lower()
            except Exception:
                pass
        return None
