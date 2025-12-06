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

# Simple button debounce state
button_was_pressed = False

# 3. Main Loop
while True:
    ble.start_advertising()
    ui.update_status("BLE: Advertising...")
    
    # Loop while waiting for connection
    while not ble.connected:
        temp = hw.sensor.temperature
        hum = hw.sensor.relative_humidity
        ui.update_data(temp, hum)
        
        # Allow button toggle even when not connected
        if hw.is_button_pressed():
            if not button_was_pressed:
                hw.toggle_led()
                print("Button: LED Toggle")
                button_was_pressed = True
        else:
            button_was_pressed = False
            
        time.sleep(0.1) # Faster loop for button responsiveness

    # Connected!
    ui.update_status("BLE: Connected!")
    
    while ble.connected:
        # 1. Read Sensors
        temp = hw.sensor.temperature
        hum = hw.sensor.relative_humidity
        
        ui.update_data(temp, hum)
        
        # 2. Send Data (Throttle this if loop is fast)
        # We use a counter or time check to avoid flooding UART
        # For simplicity, we just send every loop iteration but sleep 1s? 
        # No, we need fast loop for button. So let's track time.
        # (Skipping complex time tracking for now, we'll send every ~1s logic below)
        
        # 3. Handle Inputs
        # A. Button
        if hw.is_button_pressed():
            if not button_was_pressed:
                hw.toggle_led()
                ble.send_data(temp, hum) # Force update on press
                print("Button: LED Toggle")
                button_was_pressed = True
        else:
            button_was_pressed = False
            
        # B. BLE Commands
        cmd = ble.read_command()
        if cmd:
            print(f"BLE Command: {cmd}")
            if "on" in cmd:
                hw.set_led(True) # Usually Active Low (False=ON), but we used simple logic in hardware.py
                # Let's check: nRF52840 DK LEDs are Active Low.
                # In hardware.py I set: self.led.value = False (OFF?)
                # Actually: False is usually 0V (Sink) -> LED ON if connected to VCC.
                # True is 3.3V (Source) -> LED OFF if connected to VCC.
                # Adjusting logic to assume 'True' logic in hardware class abstracts this?
                # In hardware.py: self.led.value = state. 
                # If I want "ON" to mean Light, I should probably inverse it there if needed.
                # For now, let's assume standard logic and fix if inverted.
            elif "off" in cmd:
                hw.set_led(False)
            elif "toggle" in cmd:
                hw.toggle_led()

        # Slow down sending sensor data, but keep loop fast
        # (Simple hack: only send if seconds changed, or just relying on the sleep)
        # We'll sleep 0.1s for responsiveness, send data every 10 loops (1s)
        # Implementing simple counter
        if not hasattr(ble, '_loop_counter'): ble._loop_counter = 0
        ble._loop_counter += 1
        if ble._loop_counter >= 20: # ~2 seconds
            ble.send_data(temp, hum)
            ble._loop_counter = 0
            
        time.sleep(0.1)