#!/usr/bin/fish

set DEV "/dev/ttyArchWeather"

if not test -e $DEV
    echo "❌ Device $DEV not found."
    exit 1
end

echo "🔄 Sending Soft Reboot (Ctrl+D)..."

# Configure serial port: 115200 baud, raw input/output
stty -F $DEV 115200 raw -echo -echoe -echok

# Start reading in the background (captures for 5 seconds)
# We do this BEFORE sending the command to ensure we catch the first lines of boot output
timeout 5s cat $DEV & 
set PID $last_pid

# Short sleep to let cat attach to the stream
sleep 0.2

# Send CTRL+D (ASCII 0x04) to trigger soft reboot
printf '\x04' > $DEV

# Wait for the reading process to finish (it will stop after 5s)
wait $PID

echo -e "\n✅ Done."
