#!/usr/bin/fish

set SOURCE "src/"
set DEST "/mnt/CIRCUITPY"

if not test -d $DEST
    echo "❌ Error: Board not mounted at $DEST"
    exit 1
end

echo "📦 Deploying $SOURCE to $DEST..."

# Sync files
# -r: recursive
# -v: verbose
# -u: update (skip newer files on dest)
# --delete: remove files on board that don't exist in src (keeps it clean)
# --exclude: ignore hidden files and python cache
rsync -rvu --delete --exclude='.*' --exclude='__pycache__' $SOURCE $DEST/

if test $status -eq 0
    sync # Ensure write buffers are flushed
    echo "✅ Deployment complete."
else
    echo "❌ Deployment failed."
end
