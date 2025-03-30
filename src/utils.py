# --- START OF src/utils.py ---
import time

script_start_time = time.time() # Initialize when module is loaded

def get_elapsed_time():
    """Return a formatted string with elapsed time based on module load time."""
    global script_start_time
    elapsed = time.time() - script_start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    return f"{minutes}'{seconds:02d}\""
# --- END OF src/utils.py ---
