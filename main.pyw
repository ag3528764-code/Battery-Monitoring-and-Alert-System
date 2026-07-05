import os
import json
import time
import threading
import psutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pygame import mixer

# UI styling
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

SETTINGS_FILE = "battery_settings.json"

class BatteryAlertApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("NASA Rover Battery Alert System")
        self.geometry("450x450")
        self.resizable(False, False)
        
        # --- CRITICAL CHANGE: HARDCODED YOUR DEFAULT AUDIO PATH ---
        self.threshold = 8
        self.audio_path = r"D:\my_battery.mp3"  # Default path set to your D: drive file
        self.auto_shutdown_popup = True
        self.is_monitoring = False
        
        # Load saved data if exists (it will override default if you change it later via GUI)
        self.load_settings()
        
        # Create GUI Components
        self.create_widgets()
        self.start_ui_updater()

    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="🚀 Battery Alert Monitor", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Live Battery Status Card
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=10, fill="x", padx=20)
        
        self.live_battery_label = ctk.CTkLabel(self.status_frame, text="Current Battery: --%", font=ctk.CTkFont(size=16))
        self.live_battery_label.pack(pady=10)
        
        # Threshold Slider
        self.slider_label = ctk.CTkLabel(self, text=f"Alert Threshold: {self.threshold}%", font=ctk.CTkFont(size=14))
        self.slider_label.pack(pady=(15, 5))
        
        self.slider = ctk.CTkSlider(self, from_=5, to=50, number_of_steps=45, command=self.update_slider_label)
        self.slider.set(self.threshold)
        self.slider.pack(pady=5)
        
        # Audio File Chooser Row
        self.audio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.audio_frame.pack(pady=15, fill="x", padx=40)
        
        self.btn_browse = ctk.CTkButton(self.audio_frame, text="Change Alert Audio", command=self.browse_audio, width=140)
        self.btn_browse.pack(side="left", padx=5)
        
        self.audio_label = ctk.CTkLabel(self.audio_frame, text=self.get_short_audio_name(), text_color="gray", anchor="w")
        self.audio_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Shutdown Popup Checkbox
        self.shutdown_cb = ctk.CTkCheckBox(self, text="Show Alt+F4 Shutdown Dialog when music ends", command=self.toggle_shutdown_option)
        if self.auto_shutdown_popup:
            self.shutdown_cb.select()
        self.shutdown_cb.pack(pady=10)
        
        # Master Control Action Button
        self.btn_action = ctk.CTkButton(self, text="Start Background Service", fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(weight="bold"), command=self.toggle_monitoring)
        self.btn_action.pack(pady=25, ipadx=10, ipady=5)

    def update_slider_label(self, value):
        self.threshold = int(value)
        self.slider_label.configure(text=f"Alert Threshold: {self.threshold}%")
        self.save_settings()

    def toggle_shutdown_option(self):
        self.auto_shutdown_popup = bool(self.shutdown_cb.get())
        self.save_settings()

    def browse_audio(self):
        file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file:
            self.audio_path = file
            self.audio_label.configure(text=self.get_short_audio_name())
            self.save_settings()

    def get_short_audio_name(self):
        return os.path.basename(self.audio_path) if self.audio_path else "No audio selected"

    def save_settings(self):
        data = {"threshold": self.threshold, "audio_path": self.audio_path, "auto_shutdown_popup": self.auto_shutdown_popup}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.threshold = data.get("threshold", 8)
                    # Use saved path, fallback to default D:\ if settings file is fresh/empty
                    self.audio_path = data.get("audio_path", r"D:\my_battery.mp3")
                    self.auto_shutdown_popup = data.get("auto_shutdown_popup", True)
            except Exception:
                pass

    def start_ui_updater(self):
        def update_loop():
            while True:
                battery = psutil.sensors_battery()
                if battery:
                    status = "Plugged In" if battery.power_plugged else "Discharging"
                    self.live_battery_label.configure(text=f"Current Battery: {battery.percent}% ({status})")
                time.sleep(5)
        threading.Thread(target=update_loop, daemon=True).start()

    def toggle_monitoring(self):
        if not self.is_monitoring:
            if not self.audio_path or not os.path.exists(self.audio_path):
                messagebox.showerror("Error", f"Could not find audio at: {self.audio_path}\nMake sure file extension (.mp3/.wav) matches correctly!")
                return
            self.is_monitoring = True
            self.btn_action.configure(text="Stop Background Service", fg_color="red", hover_color="darkred")
            threading.Thread(target=self.background_monitor_worker, daemon=True).start()
            messagebox.showinfo("Activated", "Monitoring service is now running in the background!")
        else:
            self.is_monitoring = False
            self.btn_action.configure(text="Start Background Service", fg_color="green", hover_color="darkgreen")

    def background_monitor_worker(self):
        alert_played = False
        while self.is_monitoring:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                is_plugged = battery.power_plugged
                
                if percent <= self.threshold and not is_plugged:
                    if not alert_played:
                        alert_played = True
                        self.trigger_alert_sequence()
                else:
                    alert_played = False 
            time.sleep(15)

    def trigger_alert_sequence(self):
        try:
            mixer.init()
            mixer.music.load(self.audio_path)
            mixer.music.play()
            while mixer.music.get_busy() and self.is_monitoring:
                time.sleep(1)
        except Exception as e:
            print(f"Audio Error: {e}")

        # The Exact Alt + F4 System Menu Trigger
        if self.auto_shutdown_popup and self.is_monitoring:
            cmd = 'powershell -Command "(New-Object -ComObject Shell.Application).ShutdownWindows()"'
            os.system(cmd)

if __name__ == "__main__":
    app = BatteryAlertApp()
    app.mainloop()