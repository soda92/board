import board
import busio
import time
import displayio
import terminalio
import i2cdisplaybus
from adafruit_display_text import label
import adafruit_displayio_ssd1306  # <--- CONFIRMED WORKING DRIVER
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# 1. Boot Safety (Prevents "Black Screen on Plug-in")
displayio.release_displays()
time.sleep(1.5)

# 2. Setup I2C
# We stick to 400kHz since SSD1306 handles it well
i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)

# 3. Setup Display (SSD1306)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
WIDTH = 128
HEIGHT = 64
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# 4. UI Setup
splash = displayio.Group()
display.root_group = splash

title = label.Label(terminalio.FONT, text="ArchWeather", color=0xFFFFFF, x=8, y=8)
status = label.Label(terminalio.FONT, text="Init Sensor...", color=0xFFFFFF, x=8, y=25)
data_text = label.Label(
    terminalio.FONT, text="", color=0xFFFFFF, x=8, y=45, line_spacing=0.9
)

splash.append(title)
splash.append(status)
splash.append(data_text)

# 5. Setup Sensor (With Retry Logic)
bme280 = None
while bme280 is None:
    try:
        # Try standard address 0x76
        try:
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        except ValueError:
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)
    except Exception:
        status.text = "Sensor Error!"
        print("Retrying sensor...")
        time.sleep(1)

status.text = "Sensor OK!"
time.sleep(0.5)

# 6. BLE Setup
ble = BLERadio()
ble.name = "ArchWeather"
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

print("System Online.")

# 7. Main Loop
while True:
    ble.start_advertising(advertisement)
    status.text = "BLE: Advertising..."

    # Loop while waiting for connection
    while not ble.connected:
        temp = bme280.temperature
        hum = bme280.relative_humidity

        # Update OLED
        data_text.text = f"{temp:.1f} C   {hum:.0f} %"
        time.sleep(1)

    # Connected!
    status.text = "BLE: Connected!"

    while ble.connected:
        temp = bme280.temperature
        hum = bme280.relative_humidity

        # Update OLED
        data_text.text = f"{temp:.1f} C   {hum:.0f} %"

        # Send to Arch Linux
        try:
            # CSV format for your python script
            payload = f"{temp:.2f},{hum:.2f}\n"
            uart.write(payload.encode("utf-8"))
            print(f"Sent: {payload.strip()}")
        except Exception:
            pass

        time.sleep(1)
