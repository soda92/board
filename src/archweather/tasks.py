import asyncio
from archweather.state import state


async def led_task(hw):
    print("Task: LED started")
    while True:
        if state.led_mode == "scroll":
            # 1 -> 2 -> 4 -> 3
            sequence = [0, 1, 3, 2]
            for idx in sequence:
                if state.led_mode != "scroll":
                    break

                hw.set_led(idx, True)
                await asyncio.sleep(0.15)
                hw.set_led(idx, False)
        else:
            # Static Mode
            for i in range(4):
                hw.set_led(i, state.led_values[i])
            await asyncio.sleep(0.1)


async def sensor_task(hw, ui, ble):
    print("Task: Sensor started")
    while True:
        try:
            temp = hw.sensor.temperature
            hum = hw.sensor.relative_humidity
        except Exception as e:
            print(f"Sensor Error: {e}")
            temp, hum = 0, 0

        ui.update_data(temp, hum)

        if ble.connected:
            ble.send_data(temp, hum)
            ui.update_status("BLE: Connected")
        else:
            ui.update_status("BLE: Advertising...")

        await asyncio.sleep(1)


async def input_task(hw, ble):
    print("Task: Input started")
    while True:
        # A. Button Logic (All 4 buttons)
        for i in range(4):
            if hw.is_button_pressed(i):
                if not state.buttons_pressed[i]:
                    print(f"Button {i + 1} Pressed")
                    state.buttons_pressed[i] = True

                    # Action: Toggle corresponding LED
                    state.led_mode = "static"
                    state.led_values[i] = not state.led_values[i]
            else:
                state.buttons_pressed[i] = False

        # B. BLE Logic
        cmd = ble.read_command()
        if cmd:
            print(f"BLE Command: {cmd}")
            handle_command(cmd)

        await asyncio.sleep(0.05)


async def ble_monitor_task(ble):
    while True:
        if not ble.connected and not ble.ble.advertising:
            ble.start_advertising()
        elif ble.connected and ble.ble.advertising:
            ble.stop_advertising()
        await asyncio.sleep(2)


def handle_command(cmd):
    if cmd == "scroll":
        state.led_mode = "scroll"
        return

    parts = cmd.split()
    target = 1
    action = cmd

    if len(parts) >= 2:
        try:
            if parts[0] == "all":
                target = "all"
            else:
                target = int(parts[0])
            action = parts[1]
        except ValueError:
            pass

    def update_val(idx, act):
        if act == "on":
            state.led_values[idx] = True
        elif act == "off":
            state.led_values[idx] = False
        elif act == "toggle":
            state.led_values[idx] = not state.led_values[idx]

    if target == "all":
        state.led_mode = "static"
        for i in range(4):
            update_val(i, action)
    elif isinstance(target, int) and 1 <= target <= 4:
        state.led_mode = "static"
        update_val(target - 1, action)
