import board
import busio
import time
import digitalio
import i2cdisplaybus
import adafruit_displayio_ssd1306
from adafruit_bme280 import basic as adafruit_bme280

class Hardware:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
        self.display = self._setup_display()
        self.sensor = self._setup_sensor()
        
        # Setup LEDs 1-4 (Active Low)
        self.leds = []
        for pin in [board.LED1, board.LED2, board.LED3, board.LED4]:
            led = digitalio.DigitalInOut(pin)
            led.direction = digitalio.Direction.OUTPUT
            led.value = True # Start OFF
            self.leds.append(led)

        # Setup Buttons 1-4 (Active Low, Pull Up)
        self.buttons = []
        for pin in [board.BUTTON1, board.BUTTON2, board.BUTTON3, board.BUTTON4]:
            btn = digitalio.DigitalInOut(pin)
            btn.direction = digitalio.Direction.INPUT
            btn.pull = digitalio.Pull.UP
            self.buttons.append(btn)

    def toggle_led(self, index=0):
        if 0 <= index < len(self.leds):
            self.leds[index].value = not self.leds[index].value

    def set_led(self, index, state: bool):
        # state True (ON) -> value False (Low)
        if 0 <= index < len(self.leds):
            self.leds[index].value = not state

    def is_button_pressed(self, index=0):
        if 0 <= index < len(self.buttons):
            return not self.buttons[index].value
        return False

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
