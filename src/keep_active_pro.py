import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading
import os
import sys
from PIL import Image, ImageTk, ImageSequence

def resource_path(relative_path):
    """ Get absolute path to resource, works for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def keep_awake(minutes):
    try:
        duration = int(minutes)
        if duration <= 0:
            messagebox.showerror("Invalid Input", "Please enter a positive number.")
            return
        
        messagebox.showinfo("Keeping Awake", f"Your system will stay awake for {duration} minutes.")
        app.withdraw()  # Hide the application window
        
        for _ in range(duration):
            time.sleep(60)  # Wait for 1 minute
            pyautogui.press("scrolllock")  # Simulate Scroll Lock key press
            pyautogui.press("scrolllock")  # Undo Scroll Lock change (optional)
        
        messagebox.showinfo("Done", "Awake time completed!")
        app.quit()  # Close the application after completion
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

def start_awake():
    minutes = entry.get()
    threading.Thread(target=keep_awake, args=(minutes,), daemon=True).start()

def animate_gif():
    frame_index = 0
    def update_frame():
        nonlocal frame_index
        background_label.configure(image=frames[frame_index])
        frame_index = (frame_index + 1) % len(frames)
        app.after(100, update_frame)
    update_frame()

# Initialize GUI
app = tk.Tk()
app.title("KeepActive Pro")
app.update_idletasks()

# Get screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Set window size dynamically based on screen resolution
window_width = int(screen_width * 0.5)  # 50% of screen width
window_height = int(screen_height * 0.6)  # 60% of screen height
app.geometry(f"{window_width}x{window_height}+{(screen_width - window_width) // 2}+{(screen_height - window_height) // 4}")

# Set icon
icon_path = resource_path("assets/icon.ico")
if os.path.exists(icon_path):
    app.iconbitmap(icon_path)

# Load animated GIF for UI background
gif_path = resource_path("assets/20250222_1324_KeepActive Pro Icon_storyboard_01jmpach48esb93pmbbg0zvvqd.gif")
frames = []
if os.path.exists(gif_path):
    gif_image = Image.open(gif_path)
    for frame in ImageSequence.Iterator(gif_image):
        frame = frame.resize((window_width, window_height))
        frames.append(ImageTk.PhotoImage(frame))

    background_label = tk.Label(app, image=frames[0])
    background_label.place(relwidth=1, relheight=1)  # Stretch to fill window
    animate_gif()

# Create a frame for input and button (dynamically sized)
frame_width = int(window_width * 0.5)
frame_height = int(window_height * 0.3)
frame = tk.Frame(app, bg="white", bd=5, width=frame_width, height=frame_height)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Label
tk.Label(frame, text="Enter duration (minutes):", font=("Arial", 16, "bold"), bg="white").pack(pady=15)

# Input Box
entry = tk.Entry(frame, font=("Arial", 14), width=10, justify="center")
entry.pack(pady=10)

# Start Button
start_button = tk.Button(frame, text="Start", command=start_awake, font=("Arial", 16, "bold"), bg="#28a745", fg="white", width=12)
start_button.pack(pady=15)

app.update()
app.mainloop()


