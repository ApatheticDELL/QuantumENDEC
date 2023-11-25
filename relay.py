import shutil, re, json, os

# Local imports
import check
import generation
import playout

os.system('cls' if os.name == 'nt' else 'clear')

AlertFile = check.iNotify()

file = open("relay.xml", "r")
RelayXML = "".join(line.strip() for line in file.read().splitlines())
file.close()

with open("config.json", "r") as JCfile:
    config = JCfile.read()
    JCfile.close()
ConfigData = json.loads(config)

if("<sender>NAADS-Heartbeat</sender>" in RelayXML):
    print("Heartbeat detected, running heartbeat processor...")
    check.Heartbeat(RelayXML)
    exit()
else:
    print("Checking config filter...")
    check.ConfigFilters(RelayXML, ConfigData)
    shutil.move(f"relay.xml", f"XMLhistory/{AlertFile}")
    
    print("Starting Generation...")
    InfoEN = re.search(r'<info><language>en-CA</language>\s*(.*?)\s*</info>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)
    GeneratedHeader = generation.GenerateSAME(InfoEN, ConfigData)
    
    MessageType = re.search(r'<msgType>\s*(.*?)\s*</msgType>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    BroadcastText = generation.GenerateBroadcastText(InfoEN, RelayXML, GeneratedHeader, MessageType)

    print("Generating TTS...")
    generation.GenTTS(BroadcastText, InfoEN)
    
    print("Sending to discord webhook...")
    try:
        generation.SendDiscord(GeneratedHeader, BroadcastText, ConfigData)
    except:
        print("Failed to send to discord webhook!")
    
    print("Playing out alert...")
    playout.PlayAlert(ConfigData)

print("Relay complete!")
exit()