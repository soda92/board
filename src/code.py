import asyncio
import time
import displayio
from archweather.hardware import Hardware
from archweather.ui import UserInterface
from archweather.ble import BLEManager

# Shared State
class AppState:
    def __init__(self):
        self.led_mode = "static" # "static" or "scroll"
        # Track state for 4 LEDs
        self.led_values = [False, False, False, False]
        self.button_pressed = False

state = AppState()

# --- TASKS ---

async def led_task(hw):
    print("Task: LED started")
    while True:
        if state.led_mode == "scroll":
            # 1 -> 2 -> 4 -> 3
            sequence = [0, 1, 3, 2]
            for idx in sequence:
                if state.led_mode != "scroll": break
                
                # Turn ON
                hw.set_led(idx, True)
                await asyncio.sleep(0.15)
                
                # Turn OFF
                hw.set_led(idx, False)
                
            # Small pause between cycles?
            # await asyncio.sleep(0.1)
        else:
            # Static Mode: Apply stored values
            for i in range(4):
                hw.set_led(i, state.led_values[i])
            
            # Sleep to yield control, checking frequency can be low for static
            await asyncio.sleep(0.1)

async def sensor_task(hw, ui, ble):
    print("Task: Sensor started")
    while True:
        # 1. Read Sensor
        try:
            temp = hw.sensor.temperature
            hum = hw.sensor.relative_humidity
        except Exception as e:
            print(f"Sensor Error: {e}")
            temp, hum = 0, 0
            
        # 2. Update UI
        ui.update_data(temp, hum)
        
        # 3. Send BLE (if connected)
        if ble.connected:
            ble.send_data(temp, hum)
            ui.update_status("BLE: Connected")
        else:
            ui.update_status("BLE: Advertising...")
            
        # Read every 1 second
        await asyncio.sleep(1)

async def input_task(hw, ble):
    print("Task: Input started")
    while True:
        # A. Button Logic (Toggle LED 1)
        if hw.is_button_pressed():
            if not state.button_pressed:
                print("Button Pressed")
                state.button_pressed = True
                
                # Action: Toggle LED 1 (Index 0)
                # If we are scrolling, stop scrolling? Or just toggle logic?
                # Let's say button forces "static" mode and toggles LED 1
                state.led_mode = "static"
                state.led_values[0] = not state.led_values[0]
        else:
            state.button_pressed = False
            
        # B. BLE Logic
        cmd = ble.read_command()
        if cmd:
            print(f"BLE Command: {cmd}")
            handle_command(cmd, hw)
            
        # Check inputs frequently (debounce limit handled by sleep)
        await asyncio.sleep(0.05)

def handle_command(cmd, hw):
    # Special: "scroll"
    if cmd == "scroll":
        state.led_mode = "scroll"
        return

    # Normal: "1 on", "all off"
    parts = cmd.split()
    target = 1
    action = cmd
    
    if len(parts) >= 2:
        try:
            if parts[0] == "all": target = "all"
            else: target = int(parts[0])
            action = parts[1]
        except ValueError: pass

    # Apply to state
    def update_val(idx, act):
        if act == "on": state.led_values[idx] = True
        elif act == "off": state.led_values[idx] = False
        elif act == "toggle": state.led_values[idx] = not state.led_values[idx]

    if target == "all":
        state.led_mode = "static"
        for i in range(4): update_val(i, action)
    elif isinstance(target, int) and 1 <= target <= 4:
        state.led_mode = "static"
        update_val(target - 1, action)


async def main():
    # 1. Boot Safety
    displayio.release_displays()
    
    # 2. Init Hardware
    print("Initializing...")
    hw = Hardware()
    ui = UserInterface(hw.display)
    ble = BLEManager()
    
    ui.update_status("System Online")
    
    # 3. Create Tasks
    # We must explicitly start advertising before the loop or inside a task
    # The BLEManager helper assumes we call start/stop manually.
    # Let's modify it to be persistent or handle it in input/monitor task?
    # Simple fix: Start advertising and let the library handle reconnects usually.
    # But BLERadio needs start_advertising() called again after disconnect.
    
    # Let's add a small background routine to manage BLE advertising
    async def ble_monitor_task():
        while True:
            if not ble.connected and not ble.ble.advertising:
                ble.start_advertising()
            elif ble.connected and ble.ble.advertising:
                ble.stop_advertising() # Should stop automatically but good to be sure
            await asyncio.sleep(2)

    await asyncio.gather(
        led_task(hw),
        sensor_task(hw, ui, ble),
        input_task(hw, ble),
        ble_monitor_task()
    )

if __name__ == "__main__":
    asyncio.run(main())
