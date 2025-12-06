import board
import busio
import time
import i2cdisplaybus
import adafruit_displayio_ssd1306
from adafruit_bme280 import basic as adafruit_bme280

class Hardware:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
        self.display = self._setup_display()
        self.sensor = self._setup_sensor()

    def _setup_display(self):
        display_bus = i2cdisplaybus.I2CDisplayBus(self.i2c, device_address=0x3C)
        return adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

    def _setup_sensor(self):
        # Retry logic is good to keep here
        sensor = None
        attempts = 0
        while sensor is None and attempts < 5:
            try:
                try:
                    sensor = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=0x76)
                except ValueError:
                    sensor = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=0x77)
            except Exception:
                print("Retrying sensor...")
                time.sleep(1)
                attempts += 1
        
        if sensor is None:
            raise RuntimeError("Could not initialize BME280 sensor")
            
        return sensor
