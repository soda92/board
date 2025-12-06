import supervisor

# Disable auto-reload to prevent USB instability during writes
supervisor.runtime.autoreload = False

print("Boot: Auto-reload disabled.")
