#!/usr/bin/fish

set SOURCE "src/"
# Find the device with LABEL="CIRCUITPY"
set DEV (lsblk -o PATH,LABEL -n -r | grep " CIRCUITPY" | cut -d ' ' -f1)

if test -z "$DEV"
    echo "❌ Error: CIRCUITPY device not found."
    exit 1
end

set MOUNTPOINT "/mnt/tmp_circuitpy"

echo "📦 Found board at $DEV"

# Create temp mount point
if not test -d $MOUNTPOINT
    sudo mkdir -p $MOUNTPOINT
end

# Mount
# Using specific user/group to ensure write access
set UID (id -u)
set GID (id -g)
sudo mount -o uid=$UID,gid=$GID $DEV $MOUNTPOINT
if test $status -ne 0
    echo "❌ Error: Failed to mount $DEV"
    exit 1
end

echo "📂 Mounted at $MOUNTPOINT. Syncing..."

# Sync files
rsync -rvu --delete --exclude='.*' --exclude='__pycache__' $SOURCE $MOUNTPOINT/

if test $status -eq 0
    echo "✅ Sync successful."
else
    echo "❌ Sync failed."
end

# Unmount
sudo umount $MOUNTPOINT
echo "⏏️  Unmounted."