import displayio
import terminalio
from adafruit_display_text import label

class UserInterface:
    def __init__(self, display):
        self.display = display
        
        # Setup Groups
        self.splash = displayio.Group()
        self.display.root_group = self.splash

        # Setup Labels
        self.title = label.Label(terminalio.FONT, text="ArchWeather", color=0xFFFFFF, x=8, y=8)
        self.status = label.Label(terminalio.FONT, text="Init...", color=0xFFFFFF, x=8, y=25)
        self.data_text = label.Label(
            terminalio.FONT, text="--.- C   -- %", color=0xFFFFFF, x=8, y=45, line_spacing=0.9
        )

        self.splash.append(self.title)
        self.splash.append(self.status)
        self.splash.append(self.data_text)

    def update_status(self, text):
        self.status.text = text

    def update_data(self, temp, humidity):
        self.data_text.text = f"{temp:.1f} C   {humidity:.0f} %"
