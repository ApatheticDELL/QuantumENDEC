#QuantumENDEC
#By ApatheticDELL, Aaron (secludedfox.com) :3, and BunnyTub (gadielisawesome)
#I still credit Aaron and BunnyTub because some of their code from previous versions transferred onto here!

import sys
if sys.version_info.major >= 3: pass
else: print("You are not running this program with Python 3, run it with Python 3. (Or update python)"); exit()

try:
    import re, pyttsx3, requests, shutil, time, socket, threading, json, os, argparse, base64, pygame
    import sounddevice as sd
    import scipy.io.wavfile as wav
    from datetime import datetime, timezone
    from urllib.request import Request, urlopen
    from EASGen import EASGen
    from EAS2Text import EAS2Text
    from itertools import zip_longest
except Exception as e: print(f"IMPORT FAIL: {e}.\nOne or more modules has failed to inport, install the requirments!"); exit()
try: os.system("ffmpeg -version")
except: print("FFMPEG dosen't apper to be installed on your system, you will need to install it so it can be ran on a command line. Some functions of QuantumENDEC depend on FFMPEG"); exit()

QEversion = "4.4.1"

def Clear(): os.system('cls' if os.name == 'nt' else 'clear')

class Capture:
    def __init__(self, OutputFolder):
        self.NAAD1 = "streaming1.naad-adna.pelmorex.com"
        self.NAAD2 = "streaming2.naad-adna.pelmorex.com"
        self.OutputFolder = OutputFolder

    def receive(self, host, port, buffer, delimiter):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.settimeout(100)
            print(f"[Capture]: Connected to {host}")
            data_received = ""
            try:
                while True:
                    chunk = str(s.recv(buffer), encoding='utf-8', errors='ignore')
                    data_received += chunk
                    if delimiter in chunk:
                        CapturedSent = re.search(r'<sent>\s*(.*?)\s*</sent>', data_received, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
                        CapturedIdent = re.search(r'<identifier>\s*(.*?)\s*</identifier>', data_received, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
                        NAADsFilename = f"{CapturedSent}I{CapturedIdent}.xml"
                        with open(f"{self.OutputFolder}/{NAADsFilename}", 'w', encoding='utf-8') as file: file.write(data_received)
                        print(f"[Capture]: I captured an XML, and saved it to: {self.OutputFolder}/{NAADsFilename} | From: {host}")
                        data_received = ""
            except socket.timeout: print(f"[Capture]: Connection timed out for {host}"); return False
            except Exception as e: print(f"[Capture]: Something broke when connecting to {host}: {e}"); return False
            except: print("[Capture]: General exception occured!"); time.sleep(20); return False

    def start(self):
        NAAD = self.receive(self.NAAD1, 8080, 1024, "</alert>")
        if NAAD is False: NAAD = self.receive(self.NAAD2, 8080, 1024, "</alert>")
        if NAAD is False: print("[Capture]: Double brokey!")
        return False

class Check:
    def __init__(self):
        pass

    def Config(InfoX, ConfigData, Status, MsgType, Severity, Urgency, BroadcastImmediately):
        if ConfigData[f"status{Status}"] is False: return False
        if "Yes" in str(BroadcastImmediately): Final = True
        else:
            try:
                var1 = ConfigData[f"severity{Severity}"]
                var2 = ConfigData[f"urgency{Urgency}"]
                var3 = ConfigData[f"messagetype{MsgType}"]
                if var1 is True and var2 is True and var3 is True: Final = True
                else: Final = False
            except: Final = False
        if Final is True:
            if len(ConfigData['AllowedLocations_Geocodes']) == 0: pass
            else:
                GeocodeList = re.findall(r'<geocode>\s*<valueName>profile:CAP-CP:Location:0.3</valueName>\s*<value>\s*(.*?)\s*</value>', InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                for i in GeocodeList:
                    if i[:2] in ConfigData['AllowedLocations_Geocodes']: return True
                    if i[:3] in ConfigData['AllowedLocations_Geocodes']: return True
                    if i[:4] in ConfigData['AllowedLocations_Geocodes']: return True
                    if i in ConfigData['AllowedLocations_Geocodes']: return True
                return False
        return Final
        
    def MatchCLC(ConfigData, SAMEheader):
        if len(ConfigData['AllowedLocations_CLC']) == 0: return True
        else:
            for i in EAS2Text(SAMEheader).FIPS:
                if i[:2] in ConfigData['AllowedLocations_CLC']: return True
                if i[:3] in ConfigData['AllowedLocations_CLC']: return True
                if i[:4] in ConfigData['AllowedLocations_CLC']: return True
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
            if f"{sent}I{identifier}.xml" in os.listdir(f"{HistoryFolder}"):
                print("Heartbeat, no download: Files matched.")
            else:
                print( f"Downloading: {sent}I{identifier}.xml...")
                req1 = Request(url = f'http://{Dom1}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
                req2 = Request(url = f'http://{Dom2}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
                try: xml = urlopen(req1).read()
                except:
                    try: xml = urlopen(req2).read()
                    except: pass
                try:
                    with open(Output, "wb") as f: f.write(xml)
                except: print("Heartbeat, download aborted: a general exception occured, it could be that the URLs are temporarily unavailable.")


    def watchNotify(ListenFolder, HistoryFolder):
        def GetFolderQueue(): return os.listdir(f"{ListenFolder}")
        print(f"Waiting for an alert...")
        while True:
            ExitTicket = False
            for file in GetFolderQueue():
                if file in os.listdir(f"{HistoryFolder}"):
                    print("No relay: watch folder files matched.")
                    os.remove(f"{ListenFolder}/{file}")
                    ExitTicket = False
                else:
                    ExitTicket = True
                    break
            if ExitTicket is True: break
            else: time.sleep(1) # Wait a little bit between looking for new files
        return file

class Generate:
    def __init__(self, InfoXML, SentDate, MsgType, SAMEcallsign):
        self.InfoX = InfoXML
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
            "snowSquall":"WSW",
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
        GeocodeList = re.findall(r'<geocode>\s*<valueName>profile:CAP-CP:Location:0.3</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
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
        
        try: ORG = self.CapCatToSameOrg[re.search(r'<category>\s*(.*?)\s*</category>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)]
        except: ORG = "CIV"
        
        try: EVE = re.search(r'<eventCode>\s*<valueName>SAME</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        except:
            EVE = re.search(r'<eventCode>\s*<valueName>profile:CAP-CP:Event:0.4</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            try: EVE = self.CapEventToSameEvent[EVE]
            except: EVE = "CEM"

        try: Effective = datetime.fromisoformat(datetime.fromisoformat(re.search(r'<effective>\s*(.*?)\s*</effective>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)).astimezone(timezone.utc).isoformat()).strftime("%j%H%M")
        except: Effective = datetime.now().astimezone(timezone.utc).strftime("%j%H%M")
        
        try:
            Purge = datetime.fromisoformat(re.search(r'<effective>\s*(.*?)\s*</effective>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)[:-6]) - datetime.fromisoformat(re.search(r'<expires>\s*(.*?)\s*</expires>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)[:-6])
            hours, remainder = divmod(Purge.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            Purge = "{:02}{:02}".format(hours, minutes)
        except: Purge = "0600"
        
        if "layer:EC-MSC-SMC:1.1:Newly_Active_Areas" in str(self.InfoX):
            try: CLC = re.search(r'<valueName>layer:EC-MSC-SMC:1.1:Newly_Active_Areas</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace(',','-')
            except: CLC = self.GeoToCLC()
        else: CLC = self.GeoToCLC()
        
        if CLC == "": CLC = "000000"
        
        GeneratedHeader = f"ZCZC-{ORG}-{EVE}-{CLC}+{Purge}-{Effective}-{Callsign}-"
        return GeneratedHeader
        
    def BroadcastText(self, lang):
        try: BroadcastText = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Text</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace('\n','').replace('  ',' ')
        except:
            if lang == "fr": issue = "émis"; update = "mis à jour"; cancel = "annulé"
            else: issue = "issued"; update = "updated"; cancel = "cancelled"
            if self.MsgType == "Alert": MsgPrefix = issue
            elif self.MsgType == "Update": MsgPrefix = update
            elif self.MsgType == "Cancel": MsgPrefix = cancel
            else: MsgPrefix = "issued"
            
            if lang == "fr": Sent = datetime.fromisoformat(datetime.fromisoformat(self.Sent).astimezone(timezone.utc).isoformat()).strftime("%Hh%M %Z.")
            else: Sent = datetime.fromisoformat(datetime.fromisoformat(self.Sent).astimezone(timezone.utc).isoformat()).strftime("%H:%M %Z, %B %d, %Y.")
            
            try: EventType = re.search(r'<valueName>layer:EC-MSC-SMC:1.0:Alert_Name</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            except:
                if lang == "fr": EventType = re.search(r'<event>\s*(.*?)\s*</event>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1); EventType = f"alerte {EventType}"
                else: EventType = re.search(r'<event>\s*(.*?)\s*</event>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1); EventType = f"{EventType} alert"
            try:
                Coverage = re.search(r'<valueName>layer:EC-MSC-SMC:1.0:Alert_Coverage</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                if lang == "fr": Coverage = f"en {Coverage} pour:"
                else: Coverage = f"in {Coverage} for:"
            except:
                if lang == "fr": Coverage = "pour:"
                else: Coverage = "for:" 
            AreaDesc = re.findall(r'<areaDesc>\s*(.*?)\s*</areaDesc>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            AreaDesc = ', '.join(AreaDesc) + '.'
            try: SenderName = re.search(r'<senderName>\s*(.*?)\s*</senderName>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            except: SenderName = "an alert issuer"
            try: Description = re.search(r'<description>\s*(.*?)\s*</description>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace('\n', ' ')
            except: Description = ""
            try: Instruction = re.search(r'<instruction>\s*(.*?)\s*</instruction>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace('\n', ' ')
            except: Instruction = ""
            
            if lang == "fr": BroadcastText = f"À {Sent} {SenderName} a {MsgPrefix} une {EventType} {Coverage} {AreaDesc} {Description} {Instruction}".replace('###','').replace('  ',' ')
            else: BroadcastText = f"At {Sent} {SenderName} has {MsgPrefix} a {EventType} {Coverage} {AreaDesc} {Description} {Instruction}".replace('###','').replace('  ',' ')
        
        return BroadcastText

    def GetAudio(self, AudioLink, Output, DecodeType):
        if DecodeType == 1:
            print("Decoding audio from BASE64...")
            with open(Output, "wb") as fh:
                fh.write(base64.decodebytes(AudioLink))
        elif DecodeType == 0:
            print("Downloading audio...")
            r = requests.get(AudioLink)
            with open(Output, 'wb') as f:
                f.write(r.content)
            f.close()

    def Audio(self, BroadcastText, lang, ConfigData):
        try:
            BroadcastAudioResource = re.search(r'<resourceDesc>Broadcast Audio</resourceDesc>\s*(.*?)\s*</resource>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)
            if "<derefUri>" in BroadcastAudioResource:
                AudioLink = bytes(re.search(r'<derefUri>\s*(.*?)\s*</derefUri>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1), 'utf-8')
                AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Decode = 1
            else:
                AudioLink = re.search(r'<uri>\s*(.*?)\s*</uri>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Decode = 0
            if AudioType == "audio/mpeg": self.GetAudio(AudioLink,"PreAudio.mp3",Decode); os.system("ffmpeg -i PreAudio.mp3 PreAudio.wav"); os.remove("PreAudio.mp3")
            elif AudioType == "audio/x-ms-wma": self.GetAudio(AudioLink,"PreAudio.wma",Decode); os.system("ffmpeg -i PreAudio.wma PreAudio.wav"); os.remove("PreAudio.wma")
            elif AudioType == "audio/wave": self.GetAudio(AudioLink,"PreAudio.wav",Decode)
            elif AudioType == "audio/wav": self.GetAudio(AudioLink,"PreAudio.wav",Decode)
            os.system(f"ffmpeg -y -i PreAudio.wav -filter:a volume=2.5 Audio/audio.wav"); os.remove("PreAudio.wav")
        except:
            print("Generating TTS audio...")
            engine = pyttsx3.init()
            if ConfigData["UseDefaultVoices"] is False:
                if lang == "fr": ActiveVoice = ConfigData["VoiceFR"]
                else: ActiveVoice = ConfigData["VoiceEN"]
                voices = engine.getProperty('voices')
                ActiveVoice = next((voice for voice in voices if voice.name == ActiveVoice), None)
                if ActiveVoice: engine.setProperty('voice', ActiveVoice.id)
            engine.save_to_file(str(BroadcastText), f"Audio/audio.wav")
            engine.runAndWait()
        
    def AudioSAME(self, GeneratedHeader):
        print("Generating SAME header...")
        SAMEheader = EASGen.genEAS(header=GeneratedHeader, attentionTone=False, endOfMessage=False)
        SAMEeom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav("./Audio/same.wav", SAMEheader)
        EASGen.export_wav("./Audio/eom.wav", SAMEeom)

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
        else:
            pygame.mixer.init()
            pygame.mixer.music.load(InputFile)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()

    def AlertSAME(self):
        print("Playing out the alert with SAME...")
        if os.path.exists("./Audio/pre.wav"): self.play("./Audio/pre.wav")
        self.play("./Audio/same.wav")
        self.play("./Audio/attn.wav")
        self.play("./Audio/audio.wav")
        self.play("./Audio/eom.wav")
        if os.path.exists("./Audio/post.wav"): self.play("./Audio/post.wav")

    def AlertIntro(self):
        print("Playing out the alert in the standard boring manner...")
        if os.path.exists("./Audio/pre.wav"): self.play("./Audio/pre.wav")
        self.play("./Audio/attn.wav")
        
    def AlertAudio(self):
        self.play("./Audio/audio.wav")

    def AlertOutro(self):
        if os.path.exists("./Audio/post.wav"): self.play("./Audio/post.wav")

def SendDiscord(InputHeader, InputText, InputConfig, lang):
    if InputConfig['enable_discord_webhook'] is True:
        from discord_webhook import DiscordWebhook, DiscordEmbed
        Wcolor = InputConfig['webhook_color']
        Wauthorname = InputConfig['webhook_author_name']
        Wauthorurl = InputConfig['webhook_author_URL']
        Wiconurl = InputConfig['webhook_author_iconURL']
        Wurl = InputConfig['webhook_URL']

        if lang == "fr": eTitle = "ALERTE D'URGENCE"
        else: eTitle = "EMEGRENCY ALERT"

        print("Sending to discord webhook...")
        if len(InputText) > 2045: InputText = f"{InputText[:2045]}..."
        webhook = DiscordWebhook(url=Wurl, rate_limit_retry=True, content=InputHeader)
        embed = DiscordEmbed(title=eTitle, description=InputText, color=Wcolor,)
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
        print(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        ResultFileName = Check.watchNotify("./XMLqueue", "./XMLhistory")
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
            with open("config.json", "r") as JCfile: config = JCfile.read()
            ConfigData = json.loads(config)
            JCfile.close()
            Callsign = ConfigData['SAME_callsign']
            print(f"Hello {Callsign}")
            Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            Status = re.search(r'<status>\s*(.*?)\s*</status>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            MessageType = re.search(r'<msgType>\s*(.*?)\s*</msgType>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            PlayAlert = Playout(ConfigData)

            if ConfigData[f'PlayoutNoSAME'] is True:
                try: BroadcastImmediately = re.findall(r'<valueName>layer:SOREM:1.0:Broadcast_Immediately</valueName>\s*<value>\s*(.*?)\s*</value>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                except: BroadcastImmediately = ['No']
                Urgency = re.findall(r'<urgency>\s*(.*?)\s*</urgency>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                Severity = re.findall(r'<severity>\s*(.*?)\s*</severity>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                Final = False
                for a, b, c in zip_longest(Severity, Urgency, BroadcastImmediately, fillvalue=None):
                    if Check.Config(RelayXML, ConfigData, Status, MessageType, a, b, c) is True: Final = True
                if Final is False: print("No relay: None of its messages matched with config."); continue
                PlayAlert.AlertIntro()

            RelayXML = re.findall(r'<info>\s*(.*?)\s*</info>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            InfoProc = 0

            for InfoEN in RelayXML:
                InfoProc = InfoProc + 1
                print(f"\n...Processing <info>: {InfoProc}...\n")
                InfoEN = f"<info>{InfoEN}</info>"
                if re.search(r'<language>\s*(.*?)\s*</language>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1) == "fr-CA": lang = "fr"
                else: lang = "en"
                if ConfigData[f'relay_{lang}'] is False: print("not relaying:", lang); continue
                Urgency = re.search(r'<urgency>\s*(.*?)\s*</urgency>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Severity = re.search(r'<severity>\s*(.*?)\s*</severity>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                try: BroadcastImmediately = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Immediately</valueName>\s*<value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                except: BroadcastImmediately = "No"

                if Check.Config(InfoEN, ConfigData, Status, MessageType, Severity, Urgency, BroadcastImmediately) is False: print("No relay: Config filters reject.")
                else:
                    print("Generating text products...")
                    Gen = Generate(InfoEN, Sent, MessageType, Callsign)
                    GeneratedHeader = Gen.SAMEheader()
                    BroadcastText = Gen.BroadcastText(lang)
                    
                    if ConfigData[f'PlayoutNoSAME'] is False:
                        if Check.MatchCLC(ConfigData, GeneratedHeader) is False: print(f"No relay: CLC in generated header ({GeneratedHeader}) did not match config CLC ({ConfigData['AllowedLocations_CLC']})"); continue
                        if Check.DuplicateSAME(GeneratedHeader) is True: print("No relay: duplicate SAME header detected from a previous relay."); continue

                    print("Generating audio products...")
                    Gen.Audio(BroadcastText, lang, ConfigData)
                    if ConfigData[f'PlayoutNoSAME'] is False:
                        print(f"\n...NEW ALERT TO RELAY...\nSAME: {GeneratedHeader}, \nBroadcast Text: {BroadcastText}\nSending alert...")
                        Gen.AudioSAME(GeneratedHeader)
                        SendDiscord(GeneratedHeader, BroadcastText, ConfigData, lang)
                        PlayAlert.AlertSAME()
                    else:
                        print(f"\n...NEW ALERT TO RELAY...\nSAME Header is disabled. \nBroadcast Text: {BroadcastText}\nSending alert...")
                        if lang == "fr": SendDiscord("ALERTE D'URGENCE", BroadcastText, ConfigData, lang)
                        else: SendDiscord("EMEGRENCY ALERT", BroadcastText, ConfigData, lang)
                        PlayAlert.AlertAudio()

            if ConfigData[f'PlayoutNoSAME'] is True: PlayAlert.AlertOutro()

def Cap():
    while True:
        if Capture("./XMLqueue").start() is False: print("[Capture]: Something really really brokey..."); time.sleep(60)

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