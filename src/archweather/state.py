class AppState:
    def __init__(self):
        self.led_mode = "static" # "static" or "scroll"
        # Track state for 4 LEDs
        self.led_values = [False, False, False, False]
        # Track pressed state for 4 buttons to debounce/edge-detect
        self.buttons_pressed = [False, False, False, False]

# Global instance
state = AppState()
