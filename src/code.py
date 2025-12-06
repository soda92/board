import time
import displayio
from archweather.hardware import Hardware
from archweather.ui import UserInterface
from archweather.ble import BLEManager

# 1. Boot Safety
displayio.release_displays()
time.sleep(1.5)

# 2. Initialization
print("Initializing Hardware...")
hw = Hardware()
ui = UserInterface(hw.display)
ble = BLEManager()

print("System Online.")
ui.update_status("Sensor OK!")

# 3. Main Loop
while True:
    ble.start_advertising()
    ui.update_status("BLE: Advertising...")
    
    # Loop while waiting for connection
    while not ble.connected:
        temp = hw.sensor.temperature
        hum = hw.sensor.relative_humidity
        ui.update_data(temp, hum)
        time.sleep(1)

    # Connected!
    ui.update_status("BLE: Connected!")
    
    while ble.connected:
        temp = hw.sensor.temperature
        hum = hw.sensor.relative_humidity
        
        ui.update_data(temp, hum)
        ble.send_data(temp, hum)
            
        time.sleep(1)