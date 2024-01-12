#QuantumENDEC
#By ApatheticDELL, Aaron (secludedfox.com) :3, and BunnyTub (gadielisawesome)
#I still credit Aaron and BunnyTub because some of their code from previous versions transferred onto here!

import sys
if sys.version_info.major >= 3: pass
else: print("You are not running this program with Python 3, run it with Python 3. (Or update python)"); exit()

# Import all the crap
try:
    import re, xmltodict, pyttsx3, requests, shutil, time, socket, threading, json, os, argparse
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wav
    from datetime import datetime, timezone, timedelta
    from urllib.request import Request, urlopen
    from EASGen import EASGen
    from EAS2Text import EAS2Text
except: print("IMPORT FAIL: One or more modules has failed to inport please run QuantumENDEC with the --setup (-s) flag and install dependencies"); exit()
try: os.system("ffmpeg -version")
except: print("Uh oh, FFMPEG dosen't apper to be installed on your system, you will need to install it so it can be ran on a command line. Some functions of QuantumENDEC depend on FFMPEG"); exit()

QEversion = "4.0.2"

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
    debug(1,"Creating configuration...")
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
    debug(1,"Config has been created!")

def QEsetup():
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
        print("1 - Install dependencies\n2 - Do configuration setup\n3 - Credits")
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
                try: import sounddevice as sd
                except: print("IMPORT FAIL: One or more modules has failed to inport please run QuantumENDEC with the --setup (-s) flag and install dependencies"); exit()
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
        elif p == "3":
            Clear()
            print("QuantumENDEC Credits")
            print(f"QuantumENDEC\nVersion: {QEversion}\n\nDeveloped by:\nDell ... ApatheticDELL\nAaron ... secludedfox.com :3\nBunnyTub ... gadielisawesome")
            break
        else: err = "Sorry, please try that again..."
    exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='QuantumENDEC')
    parser.add_argument('-v', '--version', action='store_true', help='Displays QuantumENDECs version')
    parser.add_argument('-s', '--setup', action='store_true', help='Setup QuantumENDEC: Configure and install modules.')
    parser.add_argument('-d', '--debug', action='store_true', help='Print out debug messages.')
    args = parser.parse_args()
    if args.debug is True:
        def debug(level,message):
            if level == 1: level = "INFO"
            elif level == 2: level = "WARN"
            elif level == 3: level = "CAUTION"
            else: level = "UNKN"
            print(f"[{level}]: {message}")
        debug(1,"Full debug is now active!")
    else:
        def debug(level,message):
            if level == 1: pass
            elif level == 2: print(f"[WARN]: {message}")
            elif level == 3: print(f"[CAUTION]: {message}")
            else: level = "UNKN"
    if args.version is True: print(f"QuantumENDEC {QEversion}"); exit()
    if args.setup is True: QEsetup()

class Capture:
    def __init__(self):
        self.NAAD1 = "streaming1.naad-adna.pelmorex.com"
        self.NAAD2 = "streaming2.naad-adna.pelmorex.com"
        self.OutputFolder = "XMLqueue"
    
    def receive(self, host, port, buffer, delimiter):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.settimeout(100)
            debug(1,f"Connected to {host}")
            data_received = ""
            try:
                while True:
                    chunk = str(s.recv(buffer),encoding='utf-8', errors='ignore')
                    data_received += chunk
                    if delimiter in chunk: return data_received
            except socket.timeout:
                debug(2,f"Connection timed out for {host}")
                return False

    def start(self):
        NAADs = self.receive(self.NAAD1, 8080, 1024, "</alert>")
        if NAADs is False: NAADs = self.receive(self.NAAD2, 8080, 1024, "</alert>")
        if NAADs is False: return False
        try:
            CapturedSent = re.search(r'<sent>\s*(.*?)\s*</sent>', NAADs, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            CapturedIdent = re.search(r'<identifier>\s*(.*?)\s*</identifier>', NAADs, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            CapturedSent = CapturedSent.replace("-","_").replace("+", "p").replace(":","_")
            CapturedIdent = CapturedIdent.replace("-","_").replace("+", "p").replace(":","_")
            NAADsFilename = f"{CapturedSent}I{CapturedIdent}.xml"
        except: return False
        with open(f"./{self.OutputFolder}/{NAADsFilename}", 'w', encoding='utf-8') as file: file.write(NAADs)
        file.close()
        debug(1,f"I captured an XML, and saved it to: {self.OutputFolder}/{NAADsFilename}")
        return True

class Check:
    def __init__(self):
        pass

    def Config(InfoEN, ConfigData, Sent, Status, MsgType, Severity, Urgency, BroadcastImmediately):
        if ConfigData[f"status{Status}"] is False: return False
        if "Yes" in str(BroadcastImmediately): Final = True
        else:
            Final = ConfigData[f"severity{Severity}"]
            Final = ConfigData[f"urgency{Urgency}"]
            Final = ConfigData[f"messagetype{MsgType}"]
        if len(ConfigData['AllowedLocations_Geocodes']) == 0: pass
        else:
            GeocodeList = []
            try: 
                key = 0
                for i in InfoEN['info']['area']:
                    for Geocode in InfoEN['info']['area'][key]['geocode']:
                        if Geocode['valueName'] == 'profile:CAP-CP:Location:0.3': GeocodeList.append(Geocode['value'])
                    key = key + 1
            except:
                for Geocode in InfoEN['info']['area']['geocode']:
                    if Geocode['valueName'] == 'profile:CAP-CP:Location:0.3': GeocodeList.append(Geocode['value'])
            GeoMatch = False
            for i in GeocodeList:
                if i in ConfigData['AllowedLocations_Geocodes']: GeoMatch = True
            if GeoMatch is False: return False
        return Final
    
    def MatchCLC(ConfigData, SAMEheader):
        if len(ConfigData['AllowedLocations_CLC']) == 0: return True
        else:
            for i in EAS2Text(SAMEheader).FIPS:
                if i in ConfigData['AllowedLocations_CLC']: return True
            return False

    def DuplicateSAME(GeneratedHeader):
        try: f = open('SameHistory.txt', 'r')
        except:
            with open("SameHistory.txt", "a") as f: f.write(f"ZXZX-STARTER-\n")
            f.close()
            f = open('SameHistory.txt', 'r')
        if GeneratedHeader in f.read(): f.close(); return True
        f.close()
        with open("SameHistory.txt", "a") as f: f.write(f"{GeneratedHeader}\n")
        f.close()
        return False

    def Heartbeat(References, QueueFolder, HistoryFolder):
        debug(1,"Downloading alerts from recived heartbeat...")
        RefList = References.split(" ")
        for i in RefList:
            j = re.sub(r'^.*?,', '', i)
            j = j.split(",")
            sent = j[1]
            sentDT = sent.split("T", 1)[0]
            sent = sent.replace("-","_").replace("+", "p").replace(":","_")
            identifier = j[0]
            identifier = identifier.replace("-","_").replace("+", "p").replace(":","_")
            Dom1 = 'capcp1.naad-adna.pelmorex.com'
            Dom2 = 'capcp2.naad-adna.pelmorex.com'
            Output = f"{QueueFolder}/{sent}I{identifier}.xml"
            if f"{sent}I{identifier}.xml" in os.listdir(f"./{HistoryFolder}"):
                debug(1,"Heartbeat, no download: Files matched.")
            else:
                debug(1, f"Downloading: {sent}I{identifier}.xml...")
                req1 = Request(url = f'http://{Dom1}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
                req2 = Request(url = f'http://{Dom2}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
                try: xml = urlopen(req1).read()
                except:
                    try: xml = urlopen(req2).read()
                    except: pass
                f = open(Output, "wb")
                f.write(xml)
                f.close()

    def watchNotify(ListenFolder, HistoryFolder):
        debug(1,"Waiting for an alert...")
        def GetXMLQue(): return os.listdir(f"./{ListenFolder}")
        while True:
            ExitTicketCheck = False
            for file in GetXMLQue():
                if file in os.listdir(f"./{HistoryFolder}"):
                    debug(1,"No relay: watch folder files matched.")
                    os.remove(f"./{ListenFolder}/{file}")
                    exit()
                ExitTicketCheck = True
                break
            if ExitTicketCheck is True: break
            else: pass
            time.sleep(1) # Wait a little bit between looking for new files 
        return file

class Generate:
    def __init__(self, InfoXML, SentDate, MsgType, SAMEcallsign):
        self.InfoEN = InfoXML
        self.MsgType = MsgType
        self.Sent = SentDate
        self.Callsign = SAMEcallsign
        self.CapCatToSameOrg = {
            "Met": "WXR",
            "Admin": "EAS",
            "Other": "CIV",
        }
        self.CapEventToSameEvent = {
            "civilEmerg": "CEM",
            "terrorism": "CDW",
            "animalDang": "CDW",
            "wildFire": "FRW",
            "industryFire": "IFW",
            "urbanFire": "FRW",
            "forestFire": "FRW",
            "stormSurge": "SSW",
            "flashFlood": "FFW",
            "damOverflow": "DBW",
            "earthquake": "EQW",
            "magnetStorm": "CDW",
            "landslide": "FLW",
            "meteor": "CDW",
            "tsunami": "TSW",
            "lahar": "VOW",
            "pyroclasticS": "VOW",
            "pyroclasticF": "VOW",
            "volcanicAsh": "VOW",
            "chemical": "CHW",
            "biological": "BHW",
            "radiological": "RHW",
            "explosives": "HMW",
            "fallObject": "HMW",
            "drinkingWate": "CWW",
            "amber": "CAE",
            "hurricane": "HUW",
            "thunderstorm": "SVR",
            "tornado": "TOR",
            "testMessage": "ADR",
            "911Service": "TOE",
            "squall": "SMW",
            "winterStorm": "WSW",
            "snowfall": "WSW",
            "weather": "SPS",
            "temperature": "SPS",
            "rainfall": "SPS",
            "waterspout": "SMW"
        }

    def GeoToCLC(self):
        GeocodeList = []
        try: 
            key = 0
            for i in self.InfoEN['info']['area']:
                for Geocode in self.InfoEN['info']['area'][key]['geocode']:
                    if Geocode['valueName'] == 'profile:CAP-CP:Location:0.3': GeocodeList.append(Geocode['value'])
                key = key + 1
        except:
            for Geocode in self.InfoEN['info']['area']['geocode']:
                if Geocode['valueName'] == 'profile:CAP-CP:Location:0.3': GeocodeList.append(Geocode['value'])
        filepath = './GeoToCLC.csv'
        SameDict = {}
        with open(filepath) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                line = line.replace('\n', '')
                SAMESPLIT = line.split(",")
                SameDict[SAMESPLIT[0]] = SAMESPLIT[1]
                line = fp.readline()
                cnt += 1
        CLC = ""
        for i in GeocodeList:
            try:
                C = SameDict[i]
            except:
                C = ""
            if C == "":
                pass
            else:
                CLC = f"{CLC}" + f"{C},"
        # Aaron i know you're kinda gonna cringe at this, but we need it
        CLC = "".join(CLC.rsplit(",",1))
        CLC = CLC.split(",")
        CLC = "-".join(CLC)
        CLC = CLC.split("-")
        CLC = list(set(CLC))
        CLC = "-".join(CLC)
        return CLC
    
    def SAMEheader(self):
        Callsign = self.Callsign
        if len(Callsign) > 8: Callsign = "QUANTUM0"; debug(1,"Your callsign is too long.")
        elif len(Callsign) < 8: Callsign = "QUANTUM0"; debug(1,"Your callsign is too short.")
        elif "-" in Callsign: Callsign = "QUANTUM0"; debug(1,"Your callsign contains an invalid symbol.")
        try: ORG = self.CapCatToSameOrg[self.InfoEN['info']['category']]
        except: ORG = "CIV"
        try:
            for eventCode in self.InfoEN['info']['eventCode']:
                if eventCode['valueName'] == 'SAME': EVE = eventCode['value']; break
        except:
            try:
                for eventCode in self.InfoEN['info']['eventCode']:
                    if eventCode['valueName'] == 'profile:CAP-CP:Event:0.4': EVE = eventCode['value']; break
            except: EVE = self.InfoEN['info']['eventCode']['value']
            try: EVE = self.CapEventToSameEvent[EVE]
            except: EVE = "CEM"
        try: Effective = datetime.fromisoformat(datetime.fromisoformat(self.InfoEN['info']['effective']).astimezone(timezone.utc).isoformat()).strftime("%j%H%M")
        except: Effective = datetime.now().astimezone(timezone.utc).strftime("%j%H%M")
        try:
            Purge = datetime.fromisoformat(self.InfoEN['info']['expires'][:-6]) - datetime.fromisoformat(self.InfoEN['info']['effective'][:-6])
            hours, remainder = divmod(Purge.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            Purge = "{:02}{:02}".format(hours, minutes)
        except: Purge = "0600"
        hours, remainder = divmod(Purge.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        Purge = "{:02}{:02}".format(hours, minutes)
        if "layer:EC-MSC-SMC:1.1:Newly_Active_Areas" in str(self.InfoEN):
            for parameter in self.InfoEN['info']['parameter']:
                if parameter['valueName'] == 'layer:EC-MSC-SMC:1.1:Newly_Active_Areas':
                    try: CLC = parameter['value'].replace(',','-'); break
                    except: CLC = ""; break
        else: CLC = self.GeoToCLC()
        if CLC == "": CLC = "000000"
        GeneratedHeader = f"ZCZC-{ORG}-{EVE}-{CLC}+{Purge}-{Effective}-{Callsign}-"
        return GeneratedHeader
        
    def BroadcastText(self, GeneratedHeader):
        if "layer:SOREM:1.0:Broadcast_Text" in str(self.InfoEN):
            for parameter in self.InfoEN['info']['parameter']:
                if parameter['valueName'] == 'layer:SOREM:1.0:Broadcast_Text':
                    try: BroadcastText = parameter['value']; break
                    except: BroadcastText = ""; break
        else:
            if self.MsgType == "Alert": MsgPrefix = "issued"
            elif self.MsgType == "Update": MsgPrefix = "updated"
            elif self.MsgType == "Cancel": MsgPrefix = "cancelled"
            else: MsgPrefix = "issued"
            EventTitle = EAS2Text(GeneratedHeader).evntText
            Sent = datetime.fromisoformat(datetime.fromisoformat(self.Sent).astimezone(timezone.utc).isoformat()).strftime("%H:%M %Z, %B %d, %Y.")
            SenderName = Description = self.InfoEN['info']['senderName']
            try: Description = self.InfoEN['info']['description']; Description = Description.replace('\n', ' ')
            except: Description = ""
            try: Instruction = self.InfoEN['info']['instruction']; Instruction = Instruction.replace('\n', ' ')
            except: Instruction = ""
            try:
                Areas = []
                for AreaDesc in self.InfoEN['info']['area']: Areas.append(AreaDesc['areaDesc'])
                Areas = ', '.join(Areas) + '.'
            except: Areas = self.InfoEN['info']['area']['areaDesc'] + '.'
            if "layer:EC-MSC-SMC:1.0:Alert_Coverage" in str(self.InfoEN):
                for parameter in self.InfoEN['info']['parameter']:
                    if parameter['valueName'] == 'layer:EC-MSC-SMC:1.0:Alert_Coverage': regexcoverage = parameter['value']
                Coverage = f"in {regexcoverage} for:"
            else: Coverage = "for:"
            BroadcastText = f"At {Sent} {SenderName} has {MsgPrefix} {EventTitle} {Coverage} {Areas} {Description} {Instruction}".replace('###','').replace('  ',' ')
        return BroadcastText

    def GetAudio(self, AudioLink, Output):
        debug(1,"Downloading audio...")
        r = requests.get(AudioLink)
        with open(Output, 'wb') as f:
            f.write(r.content)
        f.close()
    
    def Audio(self, BroadcastText, GeneratedHeader):
        try:
            try:
                for BroadcastAudio in self.InfoEN['info']['resource']:
                    if BroadcastAudio['resourceDesc'] == 'Broadcast Audio': debug(1, "Yes broadcast audio.")
            except:
                if self.InfoEN['info']['resource']['resourceDesc'] == 'Broadcast Audio': debug(1,"Yes BroadcastAudio")
                AudioLink = self.InfoEN['info']['resource']['uri']
                AudioType = self.InfoEN['info']['resource']['mimeType']
            if AudioType == "audio/mpeg": self.GetAudio(AudioLink, "PreAudio.mp3"); os.system("ffmpeg -i PreAudio.mp3 PreAudio.wav"); os.remove("PreAudio.mp3")
            elif AudioType == "audio/x-ms-wma": self.GetAudio(AudioLink, "PreAudio.wma"); os.system("ffmpeg -i PreAudio.wma PreAudio.wav"); os.remove("PreAudio.wma")
            elif AudioType == "audio/wave": self.GetAudio(AudioLink, "PreAudio.wav")
            elif AudioType == "audio/wav": self.GetAudio(AudioLink, "PreAudio.wav")
            os.system(f"ffmpeg -y -i PreAudio.wav -filter:a volume=2.5 Audio/audio.wav"); os.remove("PreAudio.wav")
        except:
            debug(1,"Generating TTS audio...")
            engine = pyttsx3.init()
            engine.save_to_file(str(BroadcastText), "Audio/audio.wav")
            engine.runAndWait()
        debug(1,"Generating SAME header...")
        SAMEheader = EASGen.genEAS(header=GeneratedHeader, attentionTone=False, endOfMessage=False)
        SAMEeom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav("Audio/same.wav", SAMEheader)
        EASGen.export_wav("Audio/eom.wav", SAMEeom)

class Playout:
    def __init__(self, InputConfig):
        self.InputConfig = InputConfig

    def play(self, InputFile):
        #TODO, make this into a def setup, or seprate play def?
        UseSpecDevice = self.InputConfig['UseSpecifiedAudioDevice']
        SpecDevice = self.InputConfig['SpecifiedAudioDevice']
        time.sleep(0.5)
        if UseSpecDevice is True:
            sd.default.reset()
            sd.default.device = SpecDevice
            sampling_rate, audio_data = wav.read(InputFile)
            sd.play(audio_data, samplerate=sampling_rate)
            sd.wait()
        else: os.system(f"ffplay -hide_banner -loglevel warning -nodisp -autoexit {InputFile}")

    def AlertSAME(self):
        debug(1,"Playing out the alert with SAME")
        if os.path.exists("./Audio/pre.wav"): debug(1,"Playing lead in audio (Pre-Roll)..."); self.play("./Audio/pre.wav")
        debug(1,"Playing SAME header audio...")
        self.play("./Audio/same.wav")
        debug(1,"Playing attention tone...")
        self.play("./Audio/attn.wav")
        debug(1,"Playing broadcast audio...")
        self.play("./Audio/audio.wav")
        debug(1,"Playing EOM tones...")
        self.play("./Audio/eom.wav")
        if os.path.exists("./Audio/post.wav"): debug(1,"Playing lead out audio..."); self.play("./Audio/post.wav")

    def AlertSTANDARD(self):
        debug(1,"Playing out the alert in the standard boring manner.")
        if os.path.exists("./Audio/pre.wav"): debug(1,"Playing lead in audio (Pre-Roll)..."); self.play("./Audio/pre.wav")
        debug(1,"Playing attention tone...")
        self.play("./Audio/attn.wav")
        debug(1,"Playing broadcast audio...")
        self.play("./Audio/audio.wav")
        if os.path.exists("./Audio/post.wav"): debug(1,"Playing lead out audio..."); self.play("./Audio/post.wav")

    def Alert(self):
        if self.InputConfig['PlayoutNoSAME'] is True: self.AlertSTANDARD()
        else: self.AlertSAME()

def SendDiscord(InputHeader, InputText, InputConfig):
    if InputConfig['enable_discord_webhook'] is True:
        from discord_webhook import DiscordWebhook, DiscordEmbed
        Wcolor = InputConfig['webhook_color']
        Wauthorname = InputConfig['webhook_author_name']
        Wauthorurl = InputConfig['webhook_author_URL']
        Wiconurl = InputConfig['webhook_author_iconURL']
        Wurl = InputConfig['webhook_URL']
        debug(1,"Sending to discord webhook...")
        webhook = DiscordWebhook(url=Wurl, rate_limit_retry=True, content=InputHeader)
        embed = DiscordEmbed(title="EMEGRENCY ALERT // ALERTE D'URGENCE", description=InputText, color=Wcolor,)
        embed.set_author(name=Wauthorname, url=Wauthorurl, icon_url=Wiconurl)
        embed.set_footer(text="QuantumENDEC")
        webhook.add_embed(embed)
        webhook.execute()

def CheckFolder(folder_path, Clear):
    def ClearFolder(dir):
        for f in os.listdir(dir): os.remove(os.path.join(dir, f))
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    else:
        if Clear is True: ClearFolder(folder_path)

def QEstart():
    Clear()
    print(f"\nQuantumENDEC\nVersion: {QEversion}\n\nDeveloped by:\nDell ... ApatheticDELL\nAaron ... secludedfox.com :3\nBunnyTub ... gadielisawesome\n")
    with open("SameHistory.txt", "w") as f: f.write(f"ZXZX-STARTER-\n")
    f.close()
    CheckFolder('XMLqueue', True)
    CheckFolder('XMLhistory', True)
    CheckFolder('Audio', False)
    if os.path.isfile("./config.json") is True: pass
    else: debug(3,"Config not there, creating default config."); CreateConfig()
    if os.path.isfile("./Audio/attn.wav") is True: pass
    else:
        debug(2,"Attention tone is missing, downloading it.")
        response = requests.get("https://od.lk/d/MjdfMjY2MTU1ODJf/attn.wav")
        if response.status_code == 200:
            with open("./Audio/attn.wav", 'wb') as audio_file:
                audio_file.write(response.content)
        else: debug(2,"Could not get audio file, errors lay ahead.")
    if os.path.isfile("./GeoToCLC.csv") is True: pass
    else:
        debug(2,"GeoToCLC is missing, downloading it.")
        response = requests.get("https://od.lk/d/MjdfMjY2MTU1ODNf/GeoToCLC.csv")
        if response.status_code == 200:
            with open("./GeoToCLC.csv", 'wb') as audio_file:
                audio_file.write(response.content)
        else: debug(2,"Could not get file, errors lay ahead.")
    time.sleep(3)

def Relay():
    while True:
        ResultFileName = Check.watchNotify("XMLqueue", "XMLhistory")
        debug(1,f"Captured: {ResultFileName}")
        shutil.move(f"./XMLqueue/{ResultFileName}", f"./relay.xml")
        file = open("relay.xml", "r", encoding='utf-8')
        RelayXML = file.read()
        file.close()

        if "<sender>NAADS-Heartbeat</sender>" in RelayXML:
            debug(1,"Heartbeat detected...")
            References = re.search(r'<references>\s*(.*?)\s*</references>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            Check.Heartbeat(References, "XMLqueue", "XMLhistory")
        else:
            shutil.copy(f"./relay.xml", str(f"./XMLhistory/{ResultFileName}"))
            Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            Status = re.search(r'<status>\s*(.*?)\s*</status>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            MsgType = re.search(r'<msgType>\s*(.*?)\s*</msgType>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            RelayXML = re.search(r'<language>en-CA</language>\s*(.*?)\s*</info>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)
            InfoEN = xmltodict.parse(f"<info>{RelayXML}")
            Severity = InfoEN['info']['severity']
            Urgency = InfoEN['info']['urgency']
            for parameter in InfoEN['info']['parameter']:
                if parameter['valueName'] == 'layer:SOREM:1.0:Broadcast_Immediately': BroadcastImmediately = parameter['value']
            with open("config.json", "r") as JCfile: config = JCfile.read()
            ConfigData = json.loads(config)
            JCfile.close()
            Callsign = ConfigData['SAME_callsign']
            debug(1,f"Hello {Callsign}")
            if Check.Config(InfoEN, ConfigData, Sent, Status, MsgType, Severity, Urgency, BroadcastImmediately) is False: debug(1,"No relay: Config filters reject.")
            else:
                debug(1,"Generating text products...")
                Gen = Generate(InfoEN, Sent, MsgType, Callsign)
                GeneratedHeader = Gen.SAMEheader()
                if Check.MatchCLC(ConfigData, GeneratedHeader) is True:
                    if Check.DuplicateSAME(GeneratedHeader) is True: debug(1,"No relay: duplicate SAME header detected.")
                    else:
                        BroadcastText = Gen.BroadcastText(GeneratedHeader)
                        debug(1,"Generating audio products...")
                        Gen.Audio(BroadcastText, GeneratedHeader)
                        debug(1,f"New alert to relay...\nSAME:, {GeneratedHeader}, \nBroadcast Text:, {BroadcastText}")
                        debug(1,"Sending alert...")
                        SendDiscord(GeneratedHeader, BroadcastText, ConfigData)
                        Playout(ConfigData).Alert()
                else: debug(1,f"No relay: CLC in generated header ({GeneratedHeader}) did not match config CLC ({ConfigData['AllowedLocations_CLC']})")

def Cap():
    while True:
        while Capture().start() is True: pass
        else: debug(3,"Capture error, I don't know why"); time.sleep(15)

if __name__ == "__main__": 
    #QUANTUMENDEC STARTS HERE
    QEstart()
    CaptureThread = threading.Thread(target=Cap)
    RelayThread = threading.Thread(target=Relay)
    CaptureThread.start()
    RelayThread.start()
    CaptureThread.join()
    RelayThread.join()
    debug(3,"The end of QuantumENDEC")
