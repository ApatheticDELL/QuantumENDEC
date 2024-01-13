#QuantumENDEC
#By ApatheticDELL, Aaron (secludedfox.com) :3, and BunnyTub (gadielisawesome)
#I still credit Aaron and BunnyTub because some of their code from previous versions transferred onto here!

import sys
if sys.version_info.major >= 3: pass
else: print("You are not running this program with Python 3, run it with Python 3. (Or update python)"); exit()

import re, xmltodict, pyttsx3, requests, shutil, time, socket, threading, json, os, argparse
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from EASGen import EASGen
from EAS2Text import EAS2Text

try: os.system("ffmpeg -version")
except: print("Uh oh, FFMPEG dosen't appear to be installed on your system, you will need to install it so it can be ran on a command line. Some functions of QuantumENDEC depend on FFMPEG"); exit()

QEversion = "4.2.2"

def Clear(): os.system('cls' if os.name == 'nt' else 'clear')

class Capture:
    def __init__(self):
        self.NAAD1 = "streaming1.naad-adna.pelmorex.com"
        self.NAAD2 = "streaming2.naad-adna.pelmorex.com"
        self.OutputFolder = "XMLqueue"
    
    def receive(self, host, port, buffer, delimiter):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.settimeout(100)
            print(f"[Capture]: Connected to {host}")
            data_received = ""
            try:
                while True:
                    chunk = str(s.recv(buffer),encoding='utf-8', errors='ignore')
                    data_received += chunk
                    if delimiter in chunk: return data_received
            except socket.timeout:
                print(f"[Capture]: Connection timed out for {host}")
                return False
            except:
                print(f"[Capture]: Something brokey when connecting to {host}")
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
        except:
            print("[Capture]: Something brokey :P")
            return False
        with open(f"./{self.OutputFolder}/{NAADsFilename}", 'w', encoding='utf-8') as file: file.write(NAADs)
        file.close()
        print(f"[Capture]: I captured an XML, and saved it to: {self.OutputFolder}/{NAADsFilename}")
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
        print("Downloading alerts from recived heartbeat...")
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
                print("Heartbeat, no download: Files matched.")
            else:
                print( f"Downloading: {sent}I{identifier}.xml...")
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
        print("Waiting for an alert...")
        def GetFolderQueue(): return os.listdir(f"./{ListenFolder}")
        while True:
            ExitTicket = False
            for file in GetFolderQueue():
                if file in os.listdir(f"./{HistoryFolder}"):
                    print("No relay: watch folder files matched.")
                    os.remove(f"./{ListenFolder}/{file}")
                    ExitTicket = False
                else:
                    ExitTicket = True
                    break
            if ExitTicket is True: break
            else: time.sleep(1) # Wait a little bit between looking for new files
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
            "911Service": "TOE",
            "accident": "CDW",
            "admin":"ADR",
            "aircraftCras":"CDW",
            "airportClose":"CEM",
            "airQuality":"SPS",
            "airspaceClos":"CEM",
            "amber":"CAE",
            "ambulance":"CEM",
            "animalDang":"CDW",
            "animalDiseas":"CDW",
            "animalFeed":"CEM",
            "animalHealth":"CEM",
            "arcticOut":"SVS",
            "avalanche":"AVW",
            "aviation":"CEM",
            "biological":"BHW",
            "blizzard":"BZW",
            "bloodSupply":"CEM",
            "blowingSnow":"WSW",
            "bridgeClose":"CEM",
            "cable":"CEM",
            "chemical":"CHW",
            "civil":"CEM",
            "civilEmerg":"CEM",
            "civilEvent":"CEM",
            "coldWave":"SVS",
            "crime":"CDW",
            "damOverflow":"DBW",
            "dangerPerson":"CDW",
            "diesel":"CEM",
            "drinkingWate":"CWW",
            "dustStorm":"DSW",
            "earthquake":"EQW",
            "electric":"POS",
            "emergFacil":"CEM",
            "emergSupport":"CEM",
            "explosive":"HMW",
            "facility":"CEM",
            "fallObject":"HMW",
            "fire":"FRW",
            "flashFlood":"FFW",
            "flashFreeze":"FSW",
            "flood":"FLW",
            "foodSupply":"CEM",
            "forestFire":"WFW",
            "freezeDrzl":"WSW",
            "freezeRain":"WSW",
            "freezngSpray":"WSW",
            "frost":"SPS",
            "galeWind":"HWW",
            "gasoline":"CEM",
            "geophyiscal":"CEM",
            "hazmat":"BHW",
            "health":"BHW",
            "heatHumidity":"CEM",
            "heatingOil":"CEM",
            "heatWave":"CEM",
            "highWater":"CEM",
            "homeCrime":"CEM",
            "hospital":"CEM",
            "hurricane":"HUW",
            "hurricFrcWnd":"HUW",
            "ice":"CEM",
            "iceberg":"IBW",
            "icePressure":"CEM",
            "industCrime":"CEM",
            "industryFire":"IFW",
            "infectious":"DEW",
            "internet":"CEM",
            "lahar":"VOW",
            "landslide":"LSW",
            "lavaFlow":"VOW",
            "magnetStorm":"CDW",
            "marine":"SMW",
            "marineSecure":"SMW",
            "meteor":"CDW",
            "missingPer":"CEM",
            "missingVPer":"CEM",
            "naturalGas":"CEM",
            "nautical":"CEM",
            "notam":"CEM",
            "other":"CEM",
            "overflood":"FLW",
            "plant":"CEM",
            "plantInfect":"CEM",
            "product":"CEM",
            "publicServic":"CEM",
            "pyroclasFlow":"VOW",
            "pyroclaSurge":"VOW",
            "radiological":"RHW",
            "railway":"CEM",
            "rainfall":"SPS",
            "rdCondition":"CEM",
            "reminder":"CEM",
            "rescue":"CEM",
            "retailCrime":"CEM",
            "road":"CEM",
            "roadClose":"CEM",
            "roadDelay":"CEM",
            "roadUsage":"CEM",
            "rpdCloseLead":"CEM",
            "satellite":"CEM",
            "schoolBus":"CEM",
            "schoolClose":"CEM",
            "schoolLock":"CDW",
            "sewer":"CEM",
            "silver":"CEM",
            "snowfall":"WSW",
            "snowSquall":"SMW",
            "spclIce":"SPS",
            "spclMarine":"SMW",
            "squall":"SMW",
            "storm":"SVS",
            "stormFrcWnd":"SVS",
            "stormSurge":"SSW",
            "strongWind":"HWW",
            "telephone":"CEM",
            "temperature":"SPS",
            "terrorism":"CDW",
            "testMessage":"ADR",
            "thunderstorm":"SVR",
            "tornado":"TOR",
            "traffic":"CEM",
            "train":"CEM",
            "transit":"CEM",
            "tropStorm":"TRW",
            "tsunami":"TSW",
            "urbanFire":"FRW",
            "utility":"CEM",
            "vehicleCrime":"CEM",
            "volcanicAsh":"VOW",
            "volcano":"VOW",
            "volunteer":"CEM",
            "waste":"CEM",
            "water":"CEM",
            "waterspout":"SMW",
            "weather":"SPS",
            "wildFire":"FRW",
            "wind":"HWW",
            "windchill":"SPS",
            "winterStorm":"WSW"
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
        if len(Callsign) > 8: Callsign = "QUANTUM0"; print("Your callsign is too long!")
        elif len(Callsign) < 8: Callsign = "QUANTUM0"; print("Your callsign is too short!")
        elif "-" in Callsign: Callsign = "QUANTUM0"; print("Your callsign contains an invalid symbol!")
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
                    except: BroadcastText = "[error getting broadcast text]"; break
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
        print("Downloading audio...")
        r = requests.get(AudioLink)
        with open(Output, 'wb') as f:
            f.write(r.content)
        f.close()
    
    def Audio(self, BroadcastText, GeneratedHeader):
        def GenTTS(Input):
            engine = pyttsx3.init()
            engine.save_to_file(str(Input), "Audio/audio.wav")
            engine.runAndWait()
        
        try:
            try:
                for BroadcastAudio in self.InfoEN['info']['resource']:
                    if BroadcastAudio['resourceDesc'] == 'Broadcast Audio':
                        AudioLink = BroadcastAudio['uri']
                        AudioType = BroadcastAudio['mimeType']
            except:
                if self.InfoEN['info']['resource']['resourceDesc'] == 'Broadcast Audio': print("Yes BroadcastAudio")
                AudioLink = self.InfoEN['info']['resource']['uri']
                AudioType = self.InfoEN['info']['resource']['mimeType']
            try:
                if AudioType == "audio/mpeg": self.GetAudio(AudioLink, "PreAudio.mp3"); os.system("ffmpeg -i PreAudio.mp3 PreAudio.wav"); os.remove("PreAudio.mp3")
                elif AudioType == "audio/x-ms-wma": self.GetAudio(AudioLink, "PreAudio.wma"); os.system("ffmpeg -i PreAudio.wma PreAudio.wav"); os.remove("PreAudio.wma")
                elif AudioType == "audio/wave": self.GetAudio(AudioLink, "PreAudio.wav")
                elif AudioType == "audio/wav": self.GetAudio(AudioLink, "PreAudio.wav")
                os.system(f"ffmpeg -y -i PreAudio.wav -filter:a volume=2.5 Audio/audio.wav"); os.remove("PreAudio.wav")
            except:
                GenTTS(BroadcastText)
        except:
            print("Generating TTS audio...")
            GenTTS(BroadcastText)
            
        print("Generating SAME header...")
        SAMEheader = EASGen.genEAS(header=GeneratedHeader, attentionTone=False, endOfMessage=False)
        SAMEeom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav("Audio/same.wav", SAMEheader)
        EASGen.export_wav("Audio/eom.wav", SAMEeom)

class Playout:
    def __init__(self, InputConfig):
        self.InputConfig = InputConfig

    def play(self, InputFile):
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
        print("Playing out the alert with SAME...")
        if os.path.exists("./Audio/pre.wav"): self.play("./Audio/pre.wav")
        self.play("./Audio/same.wav")
        self.play("./Audio/attn.wav")
        self.play("./Audio/audio.wav")
        self.play("./Audio/eom.wav")
        if os.path.exists("./Audio/post.wav"): self.play("./Audio/post.wav")

    def AlertSTANDARD(self):
        print("Playing out the alert in the standard boring manner...")
        if os.path.exists("./Audio/pre.wav"): self.play("./Audio/pre.wav")
        self.play("./Audio/attn.wav")
        self.play("./Audio/audio.wav")
        if os.path.exists("./Audio/post.wav"): self.play("./Audio/post.wav")

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
        print("Sending to discord webhook...")
        webhook = DiscordWebhook(url=Wurl, rate_limit_retry=True, content=InputHeader)
        embed = DiscordEmbed(title="EMEGRENCY ALERT // ALERTE D'URGENCE", description=InputText, color=Wcolor,)
        embed.set_author(name=Wauthorname, url=Wauthorurl, icon_url=Wiconurl)
        embed.set_footer(text="QuantumENDEC")
        webhook.add_embed(embed)
        webhook.execute()
    else: print("Discord webhook is disabled! Didn't send anything.")

def CheckFolder(folder_path, Clear):
    def ClearFolder(dir):
        for f in os.listdir(dir): os.remove(os.path.join(dir, f))
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    else:
        if Clear is True: ClearFolder(folder_path)

def setup():
    Clear()
    print(f"\nQuantumENDEC\nVersion: {QEversion}\n\nDeveloped by:\nDell ... ApatheticDELL\nAaron ... secludedfox.com :3\nBunnyTub ... gadielisawesome\n")
    with open("SameHistory.txt", "w") as f: f.write(f"ZXZX-STARTER-\n")
    f.close()
    CheckFolder('XMLqueue', True)
    CheckFolder('XMLhistory', True)
    CheckFolder('Audio', False)
    if os.path.isfile("./config.json") is True: pass
    else: print("Can't find config file, please create one! I can't continue without it!"); exit()
    if os.path.isfile("./Audio/attn.wav") is True: pass
    else: print("The attention tone is missing! I can't continue without it."); exit()
    if os.path.isfile("./GeoToCLC.csv") is True: pass
    else: print("GeoToCLC is missing! I can't continue without it."); exit()
    time.sleep(3)

def Relay():
    while True:
        Clear()
        ResultFileName = Check.watchNotify("XMLqueue", "XMLhistory")
        print(f"Captured: {ResultFileName}")
        shutil.move(f"./XMLqueue/{ResultFileName}", f"./relay.xml")
        file = open("relay.xml", "r", encoding='utf-8')
        RelayXML = file.read()
        file.close()

        if "<sender>NAADS-Heartbeat</sender>" in RelayXML:
            print("\n\n...HEARTBEAT DETECTED...")
            References = re.search(r'<references>\s*(.*?)\s*</references>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            Check.Heartbeat(References, "XMLqueue", "XMLhistory")
        else:
            print("\n\n...NEW ALERT DETECTED...")
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
            print(f"Hello {Callsign}")
            if Check.Config(InfoEN, ConfigData, Sent, Status, MsgType, Severity, Urgency, BroadcastImmediately) is False: print("No relay: Config filters reject.")
            else:
                print("Generating text products...")
                Gen = Generate(InfoEN, Sent, MsgType, Callsign)
                GeneratedHeader = Gen.SAMEheader()
                if Check.MatchCLC(ConfigData, GeneratedHeader) is True:
                    if Check.DuplicateSAME(GeneratedHeader) is True: print("No relay: duplicate SAME header detected.")
                    else:
                        BroadcastText = Gen.BroadcastText(GeneratedHeader)
                        print("Generating audio products...")
                        Gen.Audio(BroadcastText, GeneratedHeader)
                        print(f"\n...NEW ALERT TO RELAY...\nSAME:, {GeneratedHeader}, \nBroadcast Text:, {BroadcastText}\n")
                        print("Sending alert...")
                        SendDiscord(GeneratedHeader, BroadcastText, ConfigData)
                        Playout(ConfigData).Alert()
                else: print(f"No relay: CLC in generated header ({GeneratedHeader}) did not match config CLC ({ConfigData['AllowedLocations_CLC']})")

def Cap():
    while True:
        while Capture().start() is True: pass
        else: print("Capture error, I don't know why"); time.sleep(15)

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='QuantumENDEC')
    parser.add_argument('-v', '--version', action='store_true', help='Displays QuantumENDECs version and exits.')
    parser.add_argument('-k', '--keepScreen', action='store_true', help='Prevents the terminal screen from clearing')
    args = parser.parse_args()
    if args.keepScreen is True:
        def Clear(): pass
    if args.version is True: print(f"QuantumENDEC {QEversion}"); exit()

    #QUANTUMENDEC STARTS HERE
    setup()
    CaptureThread = threading.Thread(target=Cap)
    RelayThread = threading.Thread(target=Relay)
    CaptureThread.start()
    RelayThread.start()
    CaptureThread.join()
    RelayThread.join()
    print("The end of QuantumENDEC")