#This is the setup script for QuantumENDEC
try:
    import json, os
    import sounddevice as sd
except: print("IMPORT FAIL: One or more modules has failed to inport please run QuantumENDEC with the --setup (-s) flag and install dependencies"); exit()

def Clear(): os.system('cls' if os.name == 'nt' else 'clear')

def CreateConfig(SameCallsign="QUANTUM8",
                 UseSpcAudio=False, SpcAudio="",
                 PlayNoSAME=False,
                 discWeb=False, dwCol="ffffff", dwAutNam="QUANTUMENDEC", dwAuURL="", dwAuIcoURL="", dwWebURL="", 
                 statTest=True, statActual=True,
                 mestypAlert=True, mestypUpdate=True, mestypCancel=True, mestypTest=True,
                 sevrExtreme=True, sevrSevere=True, sevrModerate=True, sevrMinor=True, sevrUnknown=True,
                 urgImmediate=True, urgExpected=True, urgFuture=True, urgPast=True,
                 GeoCods=[], CLC=[]):
    NewConfig = {
        "SAME_callsign": SameCallsign,
    
        "UseSpecifiedAudioDevice": UseSpcAudio,
        "SpecifiedAudioDevice": SpcAudio,

        "PlayoutNoSAME": PlayNoSAME,
        
        "enable_discord_webhook": discWeb,
        "webhook_color": dwCol,
        "webhook_author_name": dwAutNam,
        "webhook_author_URL": dwAuURL,
        "webhook_author_iconURL": dwAuIcoURL,
        "webhook_URL": dwWebURL,
        
        "statusTest": statTest,
        "statusActual": statActual,
        
        "messagetypeAlert": mestypAlert,
        "messagetypeUpdate": mestypUpdate,
        "messagetypeCancel": mestypCancel,
        "messagetypeTest": mestypTest,

        "severityExtreme": sevrExtreme,
        "severitySevere": sevrSevere,
        "severityModerate": sevrModerate,
        "severityMinor": sevrMinor,
        "severityUnknown": sevrUnknown,

        "urgencyImmediate": urgImmediate,
        "urgencyExpected": urgExpected,
        "urgencyFuture": urgFuture,
        "urgencyPast": urgPast,

        "AllowedLocations_Geocodes": GeoCods,
        "AllowedLocations_CLC": CLC,
    }
    with open("config.json", 'w') as json_file:
        json.dump(NewConfig, json_file, indent=2)


def YesNo():
    while True:
        q = input(">")
        if q == "y" or q == "Y" or q == "yes" or q == "Yes" or q == "YES": return True
        elif q == "n" or q == "N" or q == "no" or q == "No" or q == "NO": return False
        else: print("Please try again")

requirments = [
    'EASGen',
    'EAS2Text',
    'discord_webhook',
    'pyttsx3',
    'sounddevice',
    'numpy',
    'scipy',
]

err = ""

while True:
    Clear()
    print("Hello and welcome to QuantumENDEC\nPlease select a setup option...")
    print("1 - Install dependencies\n2 - Do configuration setup")
    print(err)
    p = input(">")
    if p == "1":
        Clear()
        print("Installing dependencies...")
        for i in requirments:
            try: os.system(f"pip3 install {i}"); print(f"I've installed {i}")
            except: print(f"[!!!] I've tried installing this pip package: {i}\nBut it failed, you may need pip3 installed, try just again, or do it manually")
        break
    elif p == "2":
        Clear()
        print("Configuration setup...\nLet's setup your endec, press enter when ready.")
        input(">")
        err = ""
        while True:
            Clear()
            print("Input your callsign.")
            print(err)
            ConSet1 = input(">")
            if len(ConSet1) > 8 or len(ConSet1) < 8 or "-" in ConSet1: err = "Your callsign contains an error, please try again."
            else: break
        Clear()
        print("Do you want to output alerts using a specified audio device? (y/n)")
        print("(By default (no/false) it uses FFMPEG, which usually outputs to the default device)")
        print("! This might not work on Linux. !")
        ConSet2 = YesNo()
        if ConSet2 is True:
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
                ConSet3 = select_audio_device(int(input(">")))
                if ConSet3 is False: err = "Invalid device selection: please try again."
                else: break
        else: ConSet3 = ""
        err = ""
        while True:
            Clear()
            print("How should alerts play out?")
            print("1 - With SAME\n2 - Without SAME (only attention tone and audio)")
            print(err)
            ConSet4 = input(">")
            if ConSet4 == "1": ConSet4 = False; break
            elif ConSet4 == "2": ConSet4 = True; break
            else: err = "Input error, try again."
        Clear()
        print("Would you like to setup a discord webhook? (y/n)")
        ConSet5 = YesNo()
        if ConSet5 is True:
            print("Set up your discord webhook...")
            print("\nInput webhook color. (in hex)")
            ConSet6 = input(">")
            print("\nInput webhook author name.")
            ConSet7 = input(">")
            print("\nInput author URL. (could be to a website)")
            ConSet8 = input(">")
            print("\nInput author icon URL.")
            ConSet9 = input(">")
            print("\nInput webhook URL.")
            ConSet10 = input(">")
        else:
            ConSet6 = ""
            ConSet7 = ""
            ConSet8 = ""
            ConSet9 = ""
            ConSet10 = ""
        Clear()
        print("Alert config setup.\n")
        print("Allow status: Test? (y/n)")
        ConSet11 = YesNo()
        print("Allow status: Actual? (y/n)")
        ConSet12 = YesNo()
        print("Allow message type: Alert? (y/n)")
        ConSet13 = YesNo()
        print("Allow message type: Update? (y/n)")
        ConSet14 = YesNo()
        print("Allow message type: Cancel? (y/n)")
        ConSet15 = YesNo()
        print("Allow message type: Test? (y/n)")
        ConSet16 = YesNo()
        print("Allow severity: Extreme? (y/n)")
        ConSet17 = YesNo()
        print("Allow severity: Severe? (y/n)")
        ConSet18 = YesNo()
        print("Allow severity: Moderate? (y/n)")
        ConSet19 = YesNo()
        print("Allow severity: Minor? (y/n)")
        ConSet20 = YesNo()
        print("Allow severity: Unknown? (y/n)")
        ConSet21 = YesNo()
        print("Allow urgency: Immediate? (y/n)")
        ConSet22 = YesNo()
        print("Allow urgency: Expected? (y/n)")
        ConSet23 = YesNo()
        print("Allow urgency: Future? (y/n)")
        ConSet24 = YesNo()
        print("Allow urgency: Past? (y/n)")
        ConSet25 = YesNo()
        Clear()
        print("Do you want to filter locations via CAP-CP Geocodes? (y/n)")
        if YesNo() is True:
            print("Please input the CAP-CP location Geocodes you want to relay for. (Seprate by comma, no spaces)")
            print("! These are not FIPS or CLC, they are CAP-CP Geocodes, you may need to look them up.")
            ConSet26 = input(">")
            ConSet26 = ConSet26.split(',')
        else: ConSet26 = []
        print("Do you want to filter locations via EC's CLC (Canada's FIPS)? (y/n)")
        if YesNo() is True:
            print("Please input the CLC you want to relay for. (Seprate by comma, no spaces)")
            print("These are FIPS/CLC, used in the SAME headers.")
            ConSet27 = input(">")
            ConSet27 = ConSet27.split(',')
        else: ConSet27 = []
        CreateConfig(ConSet1,ConSet2,ConSet3,ConSet4,ConSet5,ConSet6,ConSet7,ConSet8,ConSet9,ConSet10,ConSet11,ConSet12,ConSet13,ConSet14,ConSet15,
                        ConSet16,ConSet17,ConSet18,ConSet19,ConSet20,ConSet21,ConSet22,ConSet23,ConSet24,ConSet25,ConSet26,ConSet27)
        print("Config file created!")
        break
    else: err = "Sorry, please try that again..."
exit()