import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import pywhatkit
import os
import time
import subprocess
import pathlib
import screen_brightness_control as sbc
import openai

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ================== CONFIG ==================
openai.api_key="UPLOAD API KEY YOU HAVE"

# ================== SPEECH ENGINE ==================
engine = pyttsx3.init()
engine.setProperty("rate", 165)

def speak(text):
    print("NOVA:", text)
    engine.say(text)
    engine.runAndWait()

# ================== VOICE INPUT ==================
def take_command(timeout=8, phrase_time=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time)
    try:
        command = r.recognize_google(audio)
        print("YOU:", command)
        return command.lower()
    except:
        return ""

# ================== WAKE WORD ==================
def wait_for_wake_word():
    while True:
        command = take_command(timeout=3, phrase_time=3)

        # ✅ MULTIPLE WAKE WORDS
        if "hey nova" in command or command.strip() == "nova":
            speak("Yes Aksh, Nova is listening")
            return

        time.sleep(0.4)

# ================== GREETING ==================
def wish():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning Aksh")
    elif hour < 18:
        speak("Good afternoon Aksh")
    else:
        speak("Good evening Aksh")

# ================== VOLUME CONTROL ==================
def volume_change(step):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(max(current + step, 0.0), 1.0), None)

def mute_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)

# ================== SYSTEM CONTROLS ==================
def lock_screen():
    os.system("rundll32.exe user32.dll,LockWorkStation")

def sleep_system():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def shutdown():
    os.system("shutdown /s /t 1")

def restart():
    os.system("shutdown /r /t 1")

# ================== MEMORY ==================
def remember(text):
    with open("memory.txt", "a") as f:
        f.write(text.strip() + "\n")

def recall():
    try:
        with open("memory.txt", "r") as f:
            data = f.read()
        speak("Here is what I remember")
        speak(data)
    except:
        speak("I don't remember anything yet")

# ================== FOLDERS ==================
FOLDERS = {
    "downloads": str(pathlib.Path.home() / "Downloads"),
    "documents": str(pathlib.Path.home() / "Documents"),
    "desktop": str(pathlib.Path.home() / "Desktop"),
    "pictures": str(pathlib.Path.home() / "Pictures"),
    "videos": str(pathlib.Path.home() / "Videos"),
    "music": str(pathlib.Path.home() / "Music"),
    "file explorer": "explorer.exe",
    "this pc": "explorer.exe"
}

def open_folder(command):
    for name, path in FOLDERS.items():
        if name in command:
            speak(f"Opening {name}")
            os.startfile(path)
            return True
    return False

# ================== OPEN ANY APP ==================
def open_any_app(command):
    if open_folder(command):
        return
    app_name = command.replace("open", "").strip()
    try:
        subprocess.Popen(f'start {app_name}', shell=True)
        speak(f"Opening {app_name}")
    except:
        speak("I could not find that application")

# ================== AI CHAT ==================
def ai_chat(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ================== MAIN ==================
wish()
speak("Nova is running in background. Say Nova or Hey Nova to wake me.")

while True:
    wait_for_wake_word()
    command = take_command()

    if "time" in command:
        speak(datetime.datetime.now().strftime("The time is %H:%M"))

    elif "date" in command:
        speak(datetime.datetime.now().strftime("Today is %d %B %Y"))

    elif "wikipedia" in command:
        speak("Searching Wikipedia")
        result = wikipedia.summary(command.replace("wikipedia", ""), sentences=2)
        speak(result)

    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")

    elif "open google" in command:
        webbrowser.open("https://google.com")
        speak("Opening Google")

    elif "play" in command:
        speak("Playing now")
        pywhatkit.playonyt(command.replace("play", ""))

    elif "increase volume" in command:
        volume_change(0.1)
        speak("Volume increased")

    elif "decrease volume" in command:
        volume_change(-0.1)
        speak("Volume decreased")

    elif "mute" in command:
        mute_volume()
        speak("Volume muted")

    elif "max brightness" in command:
        sbc.set_brightness(100)
        speak("Brightness set to maximum")

    elif "low brightness" in command:
        sbc.set_brightness(20)
        speak("Brightness reduced")

    elif "lock screen" in command:
        speak("Locking screen")
        lock_screen()

    elif "sleep system" in command:
        speak("System going to sleep")
        sleep_system()

    elif "shutdown laptop" in command:
        speak("Shutting down laptop")
        shutdown()

    elif "restart laptop" in command:
        speak("Restarting laptop")
        restart()

    elif command.startswith("open"):
        open_any_app(command)

    elif "remember that" in command:
        remember(command.replace("remember that", ""))
        speak("I will remember that")

    elif "what do you remember" in command:
        recall()

    elif "nova sleep" in command or "nova stop" in command:
        speak("Alright Aksh, going silent")
        time.sleep(2)

    elif command != "":
        speak(ai_chat(command))
