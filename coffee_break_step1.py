import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import ctypes
import keyboard  # pip install keyboard
from pynput import mouse  # for mouse blocking

# Global state
stored_pin = ""
main_window = None
banner_window = None
mouse_listener = None
prompt_active = False
input_blocker_thread = None

# Prevent system sleep (Windows only)
def prevent_sleep():
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

# Unlock prompt logic
def unlock_prompt():
    global banner_window, main_window, mouse_listener, prompt_active

    prompt_active = True
    try:
        entered_pin = simpledialog.askstring("Unlock", "Enter 6-digit PIN:", show='*', parent=banner_window)
        if entered_pin == stored_pin:
            keyboard.unhook_all()  # stop keyboard blocking
            if mouse_listener:
                mouse_listener.stop()
            banner_window.destroy()
            main_window.deiconify()
        else:
            messagebox.showerror("Incorrect", "Wrong PIN!")
    except:
        pass
    finally:
        prompt_active = False

# Mouse input filter
def on_mouse_event(x, y, button, pressed):
    return False  # Block all mouse input

# Start mouse + keyboard blockers
def start_input_blockers():
    global mouse_listener

    # Block all keys except: shift, enter, digits
    def block_filter(e):
        if e.name in ['shift', 'shift left', 'shift right']:
            unlock_prompt()
            return False
        if e.name in ['enter']:
            return False
        if e.name.isdigit():
            return False
        if e.name in ['windows', 'left windows', 'right windows']:
            return True  # explicitly block Windows keys
        return True  # block everything else

    keyboard.hook(lambda e: keyboard.block_key(e.name) if block_filter(e) else None)

    # Block mouse clicks
    mouse_listener = mouse.Listener(on_click=on_mouse_event)
    mouse_listener.start()

# Show the fullscreen banner
def show_banner(message, color):
    global banner_window, main_window, input_blocker_thread

    prevent_sleep()
    main_window.withdraw()

    banner_window = tk.Toplevel()
    banner_window.attributes('-fullscreen', True)
    banner_window.configure(bg=color)
    banner_window.protocol("WM_DELETE_WINDOW", lambda: None)

    label = tk.Label(banner_window, text=message,
                     fg="white" if color != "yellow" else "black",
                     bg=color, font=("Consolas", 20, "bold"))
    label.pack(expand=True)

    # Start input blockers in a thread
    input_blocker_thread = threading.Thread(target=start_input_blockers, daemon=True)
    input_blocker_thread.start()

# Button press from main UI
def on_submit():
    global stored_pin

    message = message_entry.get()
    color = color_var.get()
    pin = pin_entry.get()

    if len(pin) != 6 or not pin.isdigit():
        messagebox.showerror("Error", "PIN must be a 6-digit number")
        return

    stored_pin = pin
    show_banner(message, color)

# --- Main Setup Window ---
main_window = tk.Tk()
main_window.title("Coffee Break")
main_window.geometry("320x350")
main_window.resizable(False, False)

tk.Label(main_window, text="Enter Message:").pack(pady=(15, 0))
message_entry = tk.Entry(main_window, width=30)
message_entry.pack(pady=5)

tk.Label(main_window, text="Select Banner Color:").pack(pady=(10, 0))
color_var = tk.StringVar(value="black")
color_frame = tk.Frame(main_window)
color_frame.pack()
for color in ["red", "black", "yellow", "green"]:
    tk.Radiobutton(color_frame, text=color.capitalize(), variable=color_var, value=color).pack(anchor="w")

tk.Label(main_window, text="Enter 6-digit PIN:").pack(pady=(20, 0))
pin_entry = tk.Entry(main_window, show="*", width=10)
pin_entry.pack(pady=5)

tk.Button(main_window, text="Start Break", command=on_submit).pack(pady=20)

main_window.mainloop()
