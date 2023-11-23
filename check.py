import re, os, time, shutil
from urllib.request import Request, urlopen

def ConfigFilters(InputXML, ConfigDt):
    Final = False
    BroadI = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Immediately</valueName><value>\s*(.*?)\s*</value>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
    if "Yes" in BroadI:
        Final = True
    else:
        Final = ConfigDt[re.search(r'<status>\s*(.*?)\s*</status>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)]
        Final = ConfigDt[re.search(r'<severity>\s*(.*?)\s*</severity>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)]
        Final = ConfigDt[re.search(r'<urgency>\s*(.*?)\s*</urgency>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)]
        Final = ConfigDt[re.search(r'<msgType>\s*(.*?)\s*</msgType>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)] #new
        
    if len(ConfigDt['AllowedLocations_Geocodes']) == 0:
        pass
    else:
        Geocodes = re.findall(r'<geocode><valueName>profile:CAP-CP:Location:0.3</valueName><value>\s*(.*?)\s*</value>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        GeoMatch = False
        for i in Geocodes:
            if i in ConfigDt['AllowedLocations_Geocodes']:
                GeoMatch = True
        if GeoMatch is False:
            print("No relay... Geocode filters blocked this one.")
            exit()
    
    if Final is False:
        print("No relay... Config filters blocked this one.")
        exit()

def Heartbeat(InputXML):
    References = re.search(r'<references>\s*(.*?)\s*</references>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
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
        Output = f"XMLqueue/{sent}I{identifier}.xml"

        if f"{sent}I{identifier}.xml" in os.listdir("./XMLhistory"):
            print("Files matched... no Heartbeat download...")
            pass
        else:
            req1 = Request(
                url = f'http://{Dom1}/{sentDT}/{sent}I{identifier}.xml', 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            req2 = Request(
                url = f'http://{Dom2}/{sentDT}/{sent}I{identifier}.xml', 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
                
            try:
                xml = urlopen(req1).read()
            except:
                try:
                    xml = urlopen(req2).read()
                except:
                    pass
            f = open(Output, "wb")
            f.write(xml)
            f.close()

def iNotify():
    def GetXMLQue():
        return os.listdir("./XMLqueue")

    while True:
        ExitTicketCheck = False
        print("Waiting for alert...")
        for file in GetXMLQue():
            print(f"New alert: ({file})")
            
            if file in os.listdir("./XMLhistory"):
                print("Files matched... no relay...")
                os.remove(f"./XMLqueue/{file}")
                exit()
            
            shutil.move(f"./XMLqueue/{file}", f"./relay.xml")
            ExitTicketCheck = True
            break

        if ExitTicketCheck is True:
            break
        else:
            pass

        # Wait a little bit between looking for new files 
        time.sleep(2)
    return file
