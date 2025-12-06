import asyncio
import displayio
from archweather.hardware import Hardware
from archweather.ui import UserInterface
from archweather.ble import BLEManager
from archweather.tasks import led_task, sensor_task, input_task, ble_monitor_task


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
    await asyncio.gather(
        led_task(hw),
        sensor_task(hw, ui, ble),
        input_task(hw, ble),
        ble_monitor_task(ble),
    )


if __name__ == "__main__":
    asyncio.run(main())
