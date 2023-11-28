from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime, timezone
from EASGen import EASGen
from EAS2Text import EAS2Text
import re, pyttsx3, requests, shutil, os, base64

# local import
import Conversions

def GenerateSAME(InputXML, InputConfig):
    Callsign = InputConfig['SAME_callsign']
    if len(Callsign) > 8:
        Callsign = "QUANTUM0"
        print("Callsign contains an error, please check config... Too long")
    elif len(Callsign) < 8:
        Callsign = "QUANTUM0"
        print("Callsign contains an error, please check config... Too short")
    elif "-" in Callsign:
        Callsign = "QUANTUM0"
        print("Callsign contains an error, please check config... Invalid symbol")
    
    ORG = re.search(r'<category>\s*(.*?)\s*</category>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    try:
        ORG = Conversions.CapCatToSameOrg[ORG]
    except:
        ORG = "CIV"

    if("<valueName>SAME</valueName>" in InputXML):
        EEE = re.search(r'<eventCode><valueName>SAME</valueName><value>\s*(.*?)\s*</value>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    else:
        #Fixed to get CAP-CP event code!
        EEE = re.search(r'<eventCode><valueName>profile:CAP-CP:Event:0.4</valueName><value>\s*(.*?)\s*</value></eventCode>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        try:
            EEE = Conversions.CapEventToSameEvent[EEE]
        except:
            BroadI = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Immediately</valueName><value>\s*(.*?)\s*</value>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            if("Yes" in BroadI):
                EEE = "CEM"
            else:
                print("No avilable conversion to SAME event and is not set for broadcast immediately.")
                print("Exiting...")
                exit()
        
    def GeoToCLC():
        Geocodes = re.findall(r'<geocode><valueName>profile:CAP-CP:Location:0.3</valueName><value>\s*(.*?)\s*</value>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
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
        for i in Geocodes:
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
    
    if("EC-MSC-SMC:1.1:Newly_Active_Areas" in InputXML):
        try:
            CLC = re.search(r'<parameter><valueName>layer:EC-MSC-SMC:1.1:Newly_Active_Areas</valueName><value>\s*(.*?)\s*</value>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace(",","-")
        except:
            CLC = GeoToCLC()
    else:
        CLC = GeoToCLC()
    
    if CLC == "":
        CLC = "000000"

    if("<effective>" in InputXML):
        EffDate = re.search(r'<effective>\s*(.*?)\s*</effective>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        DT = datetime.fromisoformat(datetime.fromisoformat(EffDate).astimezone(timezone.utc).isoformat()).strftime("%j%H%M")
    else:
        DT = datetime.now().astimezone(timezone.utc)
        DT = DT.strftime("%j%H%M")

    HeaderSAME = f"ZCZC-{ORG}-{EEE}-{CLC}+0600-{DT}-{Callsign}-"

    try:
        f = open('SameHistory.txt', 'r')
    except:
        with open("SameHistory.txt", "a") as f:
            f.write(f"ZXZX-STARTER-\n")
        f.close()
        f = open('SameHistory.txt', 'r')

    if HeaderSAME in f.read():
        print("Found previous SAME header match... exiting...")
        f.close()
        exit()
    f.close()

    with open("SameHistory.txt", "a") as f:
        f.write(f"{HeaderSAME}\n")
    
    Header = EASGen.genEAS(header=HeaderSAME, attentionTone=False, endOfMessage=False)
    Eom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
    EASGen.export_wav("Audio/same.wav", Header)
    EASGen.export_wav("Audio/eom.wav", Eom)

    return HeaderSAME

def GenerateBroadcastText(InfoInputXML, FullInputXML, InputSAME):
    if("<valueName>layer:SOREM:1.0:Broadcast_Text</valueName>" in InfoInputXML):
        BroadcastText = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Text</valueName><value>\s*(.*?)\s*</value>', InfoInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    else:
        #Manually generates the BroadcastText if there's no broadcast text value
        Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', FullInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        DATE = datetime.fromisoformat(datetime.fromisoformat(Sent).astimezone(timezone.utc).isoformat()).strftime("%H:%M %Z, %B %d, %Y.")
        SENDER = re.search(r'<senderName>\s*(.*?)\s*</senderName>', InfoInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        HEADLINE = EAS2Text(InputSAME).evntText
        AREAS = re.findall(r'<areaDesc>\s*(.*?)\s*</areaDesc>', InfoInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        AREAS = ", ".join(AREAS)
        AREAS = ".".join(AREAS.rsplit(",",1))
        AREAS = AREAS + "."

        #Issued, Updated, Cancelled
        MessageType = re.search(r'<msgType>\s*(.*?)\s*</msgType>', FullInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        if MessageType == "Alert":
            MsgIssue = "issued"
        elif MessageType == "Update":
            MsgIssue = "updated"
        elif MessageType == "Cancel":
            MsgIssue = "cancelled"
        else:
            MsgIssue = "issued"

        if("layer:EC-MSC-SMC:1.0:Alert_Coverage" in InfoInputXML):
            regexcoverage = re.search(r'<valueName>layer:EC-MSC-SMC:1.0:Alert_Coverage</valueName><value>\s*(.*?)\s*</value>', InfoInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            COVERAGE = f"In {regexcoverage} for:"
        else:
            COVERAGE = "For:"

        try:
            DESCRIPTION =  re.search(r'<description>\s*(.*?)\s*</description>', InfoInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("###","")
        except:
            DESCRIPTION = ""

        try:
            INSTRUCTION =  re.search(r'<instruction>\s*(.*?)\s*</instruction>', InfoInputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("###","")
        except:
            INSTRUCTION = ""
        BroadcastText = f"At {DATE} {SENDER} has {MsgIssue} {HEADLINE} {COVERAGE} {AREAS} {DESCRIPTION}. {INSTRUCTION}."
    
    f = open("Broadcast.txt", "w")
    f.write(BroadcastText)
    f.close()

    return BroadcastText

def GenTTS(TextInput, InputInfoXML):
    if "<resourceDesc>Broadcast Audio</resourceDesc>" in InputInfoXML:
        BroadcastAudioResource = re.search(r'<resource><resourceDesc>Broadcast Audio</resourceDesc>\s*(.*?)\s*</resource>', InputInfoXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)
        if "<derefUri>" in BroadcastAudioResource:
            print("Decode base64")
            AudioLink = bytes(re.search(r'<derefUri>\s*(.*?)\s*</derefUri>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1), 'utf-8')
            AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            Decode = 1
        else:
            print("Download from web")
            AudioLink = re.search(r'<uri>\s*(.*?)\s*</uri>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            Decode = 0
        def GetAudio(Output):
            if Decode == 1:
                with open(Output, "wb") as fh:
                    fh.write(base64.decodebytes(AudioLink))
            elif Decode == 0:
                r = requests.get(AudioLink)
                with open(Output, 'wb') as f:
                    f.write(r.content)
        if AudioType == "audio/mpeg":
            GetAudio("PreAudio.mp3")
            os.system("ffmpeg -i PreAudio.mp3 PreAudio.wav")
            os.remove("PreAudio.mp3")
        elif AudioType == "audio/x-ms-wma":
            GetAudio("PreAudio.wma")
            os.system("ffmpeg -i PreAudio.wma PreAudio.wav")
            os.remove("PreAudio.wma")
        elif AudioType == "audio/wave":
            GetAudio("PreAudio.wav")
        elif AudioType == "audio/wav":
            GetAudio("PreAudio.wav")
        os.system(f"ffmpeg -y -i PreAudio.wav -filter:a volume=3.2 Audio/audio.wav")
        os.remove("PreAudio.wav")
    else:
        engine = pyttsx3.init()
        engine.save_to_file(str(TextInput), "Audio/audio.wav")
        engine.runAndWait()

def SendDiscord(InputHeader, InputText, InputConfig):
    Wcolor = InputConfig['webhook_color']
    Wauthorname = InputConfig['webhook_author_name']
    Wauthorurl = InputConfig['webhook_author_URL']
    Wiconurl = InputConfig['webhook_author_iconURL']
    Wurl = InputConfig['webhook_URL']

    if InputConfig['enable_discord_webhook'] is True:
        print("Sending to discord webhook...")
        webhook = DiscordWebhook(url=Wurl, rate_limit_retry=True, content=InputHeader)
        embed = DiscordEmbed(title="EMEGRENCY ALERT // ALERTE D'URGENCE", description=InputText, color=Wcolor,)
        embed.set_author(name=Wauthorname, url=Wauthorurl, icon_url=Wiconurl)
        embed.set_footer(text="QuantumENDEC")
        webhook.add_embed(embed)
        webhook.execute()
    else:
        print("Discord webhook not configured.")
