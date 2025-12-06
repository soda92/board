#!/usr/bin/fish

set DEVICE "/dev/ttyArchWeather"

echo "🔌 Waiting for $DEVICE..."

while true
    if test -e $DEVICE
        echo "✅ Connected to $DEVICE"
        # Use stty to configure the serial port (115200 baud, raw mode)
        stty -F $DEVICE 115200 raw -echo -echoe -echok
        # Read from the device
        cat $DEVICE
        echo "❌ Disconnected."
        sleep 1
    else
        sleep 0.5
    end
end
