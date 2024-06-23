#This is the setup script for QuantumENDEC

import json, os, time, keyboard
def Clear(): os.system('cls' if os.name == 'nt' else 'clear')

def SelectTTS(InputPre):
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("Available voices:")
    for i, voice in enumerate(voices): print(f"{i + 1}. {voice.name}")
    selected_index = int(input(f"{InputPre} > ")) - 1
    if 0 <= selected_index < len(voices): selected_voice = voices[selected_index]; return selected_voice
    else: return None

def YesNoQuestion(InputQuestion):
    err = ""
    while True:
        Clear()
        print(InputQuestion)
        print(err)
        q = input(">")
        if q == "y" or q == "Y" or q == "yes" or q == "Yes" or q == "YES": return True
        elif q == "n" or q == "N" or q == "no" or q == "No" or q == "NO": return False
        else: err = "Please try again"

def YesNo():
    while True:
        q = input(">")
        if q == "y" or q == "Y" or q == "yes" or q == "Yes" or q == "YES": return True
        elif q == "n" or q == "N" or q == "no" or q == "No" or q == "NO": return False
        else: print("Please try again")

Clear()
print("--- QUANTUMENDEC CONFIGURATION SETUP ---")
time.sleep(1)

UseSpecifiedAudioDevice = YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nDo you want to output alerts using a specified audio device? (y/n)\n(By default (no/false) it uses FFMPEG, which usually outputs to the default device\n! This might not work on Linux. !")
if UseSpecifiedAudioDevice is True:
    try: import sounddevice as sd
    except: print("IMPORT FAIL: One or more modules has failed to inport."); exit()
    def print_available_devices():
        print("Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"{i}: {device['name']} (Host API: {sd.query_hostapis()[device['hostapi']]['name']})")
    def select_audio_device(device_index):
        devices = sd.query_devices()
        if 0 <= device_index < len(devices):
            selected_device = devices[device_index]
            selected_hostapi_name = sd.query_hostapis()[selected_device['hostapi']]['name']
            sd.default.device = selected_device['name']
            return f"{selected_device['name']}, {selected_hostapi_name}"
        else: return False
    err = ""
    while True:
        Clear()
        print("\nYou will need to select an audio device.")
        print_available_devices()
        print("\nSelect output device (select number of it)")
        print(err)
        SpecifiedAudioDevice = select_audio_device(int(input(">")))
        if SpecifiedAudioDevice is False: err = "Invalid device selection: please try again."
        else: break
else: SpecifiedAudioDevice = ""

relay_en = YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nYou can relay alerts in both English and French, or one or the other.\nDo you want to relay alerts in English? (y/n)")
relay_fr = YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nYou can relay alerts in both English and French, or one or the other.\nDo you want to relay alerts in French? (y/n)")

if YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nDo you want to set up voices? (y/n)") is True:
    UseDefaultVoices = False
    SelectVoice = None; err = ""
    while SelectVoice is None:
        Clear()
        try:
            SelectVoice = SelectTTS(f"\n{err}Select English voice (number)")
            if SelectVoice is None: err = "Invalid input, try again!\n"
            else: VoiceEN = SelectVoice.name
        except: err = "Input error, try again!\n"

    SelectVoice = None; err = ""
    while SelectVoice is None:
        Clear()
        try:
            SelectVoice = SelectTTS(f"\n{err}Select French voice (number)")
            if SelectVoice is None: err = "Invalid input, try again!\n"
            else: VoiceFR = SelectVoice.name
        except: err = "Input error, try again!\n"
    UseDefaultVoices = False
else:
    UseDefaultVoices = True
    VoiceEN = ""
    VoiceFR = ""

enable_discord_webhook = YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nWould you like to setup a discord webhook? (y/n)")
if enable_discord_webhook is True:
    print("Set up your discord webhook...")
    print("\nInput webhook color. (in hex)")
    webhook_color = input(">")
    print("\nInput webhook author name.")
    webhook_author_name = input(">")
    print("\nInput author URL. (could be to a website)")
    webhook_author_URL = input(">")
    print("\nInput author icon URL.")
    webhook_author_iconURL = input(">")
    print("\nInput webhook URL.")
    webhook_URL = input(">")
else:
    webhook_color = ""
    webhook_author_name = ""
    webhook_author_URL = ""
    webhook_author_iconURL = ""
    webhook_URL = ""

if YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nDo you want alerts to play out with S.A.M.E? (y/n)") is True:
    PlayoutNoSAME = False
    err = ""
    while True:
        Clear()
        print("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\n")
        print("Input your (S.A.M.E) callsign.")
        print(err)
        SAME_callsign = input(">")
        if len(SAME_callsign) > 8 or len(SAME_callsign) < 8 or "-" in SAME_callsign: err = "Your callsign contains an error, please try again."
        else: break

    if YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nDo you want to filter locations via EC's CLC (Canada's FIPS)? (y/n)") is True:
        print("Please input the CLC you want to relay for. (Seprate by comma, no spaces)")
        print("These are FIPS/CLC, used in the SAME headers.")
        AllowedLocations_CLC = input(">")
        AllowedLocations_CLC = AllowedLocations_CLC.split(',')
    else: AllowedLocations_CLC = []
else:
    PlayoutNoSAME = True
    SAME_callsign = "SAMELESS"
    AllowedLocations_CLC = []

if YesNoQuestion("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nDo you want to filter locations via CAP-CP Geocodes? (y/n)") is True:
    print("Please input the CAP-CP location Geocodes you want to relay for. (Seprate by comma, no spaces)")
    print("! These are not FIPS or CLC, they are CAP-CP Geocodes, you may need to look them up.")
    AllowedLocations_Geocodes = input(">")
    AllowedLocations_Geocodes = AllowedLocations_Geocodes.split(',')
else: AllowedLocations_Geocodes = []

options = {
    "A": True,
    "B": True,
    
    "C": True,
    "D": True,
    "E": True,
    "F": True,

    "0": True,
    "1": True,
    "2": True,
    "3": True,
    "4": True,

    "5": True,
    "6": True,
    "7": True,
    "8": True,
    "9": True,
}

def Clear(): os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    Clear()
    print("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nToggle True/False on the following alert relay filters.")
    print("A: Status Test:", options['A'])
    print("B: Status Actual:", options['B'])
    print("")
    print("C: Message type Alert:", options['C'])
    print("D: Message type Update:", options['D'])
    print("E: Message type Cancel:", options['E'])
    print("F: Message type Test:", options['F'])
    print("")
    print("0: Severity Extreme:", options['0'])
    print("1: Severity Severe:", options['1'])
    print("2: Severity Moderate:", options['2'])
    print("3: Severity Minor:", options['3'])
    print("4: Severity Unknown:", options['4'])
    print("")
    print("5: Urgency Immediate:", options['5'])
    print("6: Urgency Expected:", options['6'])
    print("7: Urgency Future:", options['7'])
    print("8: Urgency Past:", options['8'])
    print("9: Urgency Unknown:", options['9'])
    print("")
    print("\nPress the listed keyboard button to toggle True/False to the corresponding option. Press Enter to confirm.")

def toggle_option(key):
    if key.name.upper() in options:
        options[key.name.upper()] = not options[key.name.upper()]
        print_menu()

print_menu()
keyboard.on_press_key("a", toggle_option)
keyboard.on_press_key("b", toggle_option)
keyboard.on_press_key("c", toggle_option)
keyboard.on_press_key("d", toggle_option)
keyboard.on_press_key("e", toggle_option)
keyboard.on_press_key("f", toggle_option)
keyboard.on_press_key("0", toggle_option)
keyboard.on_press_key("1", toggle_option)
keyboard.on_press_key("2", toggle_option)
keyboard.on_press_key("3", toggle_option)
keyboard.on_press_key("4", toggle_option)
keyboard.on_press_key("5", toggle_option)
keyboard.on_press_key("6", toggle_option)
keyboard.on_press_key("7", toggle_option)
keyboard.on_press_key("8", toggle_option)
keyboard.on_press_key("9", toggle_option)
keyboard.wait('enter')
keyboard.unhook_all()

NewConfig = {
    "SAME_callsign": SAME_callsign,

    "UseSpecifiedAudioDevice": UseSpecifiedAudioDevice,
    "SpecifiedAudioDevice": SpecifiedAudioDevice,

    "PlayoutNoSAME": PlayoutNoSAME,
    "relay_en": relay_en,
    "relay_fr": relay_fr,

    "UseDefaultVoices": UseDefaultVoices,
    "VoiceEN": VoiceEN,
    "VoiceFR": VoiceFR,

    "enable_discord_webhook": enable_discord_webhook,
    "webhook_color": webhook_color,
    "webhook_author_name": webhook_author_name,
    "webhook_author_URL": webhook_author_URL,
    "webhook_author_iconURL": webhook_author_iconURL,
    "webhook_URL": webhook_URL,
    
    "statusTest": options["A"],
    "statusActual": options["B"],
    
    "messagetypeAlert": options["C"],
    "messagetypeUpdate": options["D"],
    "messagetypeCancel": options["E"],
    "messagetypeTest": options["F"],

    "severityExtreme": options["0"],
    "severitySevere": options["1"],
    "severityModerate": options["2"],
    "severityMinor": options["3"],
    "severityUnknown": options["4"],

    "urgencyImmediate": options["5"],
    "urgencyExpected": options["6"],
    "urgencyFuture": options["7"],
    "urgencyPast": options["8"],
    "urgencyUnknown": options["9"],

    "AllowedLocations_Geocodes": AllowedLocations_Geocodes,
    "AllowedLocations_CLC": AllowedLocations_CLC,
}
try:
    with open("config.json", 'w') as json_file: json.dump(NewConfig, json_file, indent=2)
    print("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nConfig file saved!")
except: print("--- QUANTUMENDEC CONFIGURATION SETUP ---\n\nError saving config file.")
time.sleep(1)