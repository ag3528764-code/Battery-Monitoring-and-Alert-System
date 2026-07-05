# Battery-Monitoring-and-Alert-System


Hey everyone! This is a simple desktop app I built using Python and CustomTkinter. It keeps an eye on your laptop's battery in the background and plays a custom alarm sound if the battery drops below a limit you choose. It can also bring up the Windows Alt+F4 shutdown menu once the music ends so you don't lose your work.

# Cool Things It Does

Modern Dark UI: Used CustomTkinter so it actually looks clean and modern instead of looking like an old school Windows 98 app.

Live Battery Tracking: It shows your current battery percentage and whether it's charging or discharging in real-time.

Slider for Threshold: You can just slide a bar to change the alert trigger anywhere from 5% to 50%.

Custom Alarm Music: You can pick any .mp3 or .wav file from your computer to play as the alarm.

Saves Your Settings: It creates a small battery_settings.json file so it remembers your custom sound path and threshold next time you open it.

No Lag/Freezing: I put the battery checking and music playing on separate background threads so the UI stays smooth and doesn't crash or freeze up.

# How to Run It
Run the script from your terminal:

Bash
python battery_alert.py
Pick your alert threshold using the slider.

Click "Change Alert Audio" to select your alarm sound file (by default it looks for D:\my_battery.mp3).

Keep the checkbox ticked if you want the Alt+F4 shutdown window to pop up when the battery gets critically low.

Hit "Start Background Service"
