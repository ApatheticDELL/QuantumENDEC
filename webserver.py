orgSAMEtoCAP = {"WXR": "Met", "EAS": "Admin", "CIV": "Other"}

eventSAMEtoCAP = {
    "TOE": "911Service",
    "CDW": "schoolLock",
    "ADR": "testMessage",
    "CEM": "volunteer",
    "SPS": "windchill",
    "CAE": "amber",
    "AVW": "avalanche",
    "BHW": "health",
    "BZW": "blizzard",
    "WSW": "winterStorm",
    "CHW": "chemical",
    "CWW": "drinkingWate",
    "DSW": "dustStorm",
    "EQW": "earthquake",
    "POS": "electric",
    "FFW": "flashFlood",
    "FSW": "flashFreeze",
    "FLW": "flood",
    "FRW": "urbanFire",
    "HWW": "wind",
    "IBW": "iceberg",
    "SVS": "stormFrcWnd",
    "DBW": "damOverflow",
    "HUW": "hurricane",
    "IFW": "industryFire",
    "DEW": "infectious",
    "LSW": "landslide",
    "VOW": "volcano",
    "SMW": "squall",
    "SSW": "stormSurge",
    "SVR": "thunderstorm",
    "TOR": "tornado",
    "TSW": "tsunami",
    "TRW": "tropStorm",
    "RHW": "radiological",
    "CEM": "publicServic",
    "WFW": "forestFire",
    "HMW": "explosive",
    "SPS": "frost",
    "HWW": "strongWind",
    "CEM": "schoolBus",
    "CEM": "satellite",
    "CEM": "roadUsage",
    "CEM": "rpdCloseLead",
    "CEM": "roadDelay",
    "CEM": "roadClose",
    "CEM": "rescue",
    "CEM": "retailCrime",
    "CEM": "railway",
    "CEM": "plantInfect",
    "CEM": "product",
    "CEM": "plant",
    "CEM": "publicServic",
    "CEM": "emergSupport",
    "CEM": "emergFacil",
    "CEM": "foodSupply",
    "CEM": "internet",
    "CEM": "industCrime",
    "CEM": "icePressure",
    "CEM": "highWater",
    "CEM": "hospital",
    "CEM": "homeCrime",
    "CEM": "geophyiscal",
    "CEM": "gasoline",
    "CEM": "heatWave",
    "CEM": "heatingOil",
    "CEM": "heatHumidity",
    "CEM": "missingPer",
    "CEM": "missingVPer",
    "CEM": "nautical",
    "CEM": "notam",
    "CEM": "other",
    "CEM": "sewer",
    "CEM": "silver",
    "CEM": "weather",
    "CEM": "water",
    "CEM": "waste",
    "CEM": "transit",
    "CEM": "train",
    "CEM": "traffic",
    "CEM": "utility",
    "CEM": "animalFeed",
    "CEM": "animalHealth",
    "CEM": "bridgeClose",
    "CEM": "biological",
    "CEM": "civil",
    "CEM": "civilEmerg",
    "CEM": "civilEvent",
    "CEM": "other",
    "CEM": "homeCrime",
    "CEM": "plant",
    "CEM": "product",
    "CEM": "publicServic",
    "CEM": "satellite",
    "CEM": "schoolBus",
    "CEM": "schoolClose",
    "CEM": "roadUsage",
    "CEM": "roadClose",
    "CEM": "roadDelay",
    "CEM": "rpdCloseLead",
    "CEM": "sewer",
    "CEM": "silver",
    "CEM": "water",
    "CEM": "waste",
    "CEM": "transit",
    "CEM": "train",
    "CEM": "traffic",
    "CEM": "utility",
    "CDW": "schoolLock",
    "CDW": "magnetStorm",
    "CDW": "meteor",
    "CDW": "animalDang",
    "CDW": "animalDiseas",
    "CDW": "dangerPerson",
    "CDW": "crime",
    "CEM": "roadUsage",
    "CDW": "terrorism",
    "RHW": "radiological",
    "RHW": "hazmat",
    "HWW": "strongWind",
    "HWW": "galeWind",
    "TRW": "tropStorm",
    "VOW": "pyroclasFlow",
    "VOW": "volcanicAsh",
    "VOW": "lavaFlow",
    "VOW": "pyroclaSurge",
    "VOW": "volcano",
    "SMW": "spclMarine",
    "SMW": "marineSecure",
    "SMW": "waterspout",
    "SMW": "squall",
    "SMW": "marine",
    "SPS": "temperature",
    "SPS": "spclIce",
    "SPS": "frost",
    "SPS": "rainfall",
    "SPS": "weather",
    "SPS": "windchill",
    "SVS": "arcticOut",
    "SVS": "coldWave",
    "SVS": "storm",
    "SVS": "stormFrcWnd",
    "SSW": "stormSurge",
    "TOR": "tornado",
    "TSW": "tsunami",
    "TRW": "tropStorm",
    "WFW": "wildFire",
    "HWW": "wind",
    "SPS": "windchill",
    "WSW": "winterStorm",
}

from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, make_response, session
import os, json, hashlib, random, string, secrets, re, pyttsx3
import sounddevice as sd
from datetime import datetime, timezone, timedelta
from EAS2Text import EAS2Text

try: import pythoncom
except: pass

app = Flask(__name__)
#app = Flask(__name__, static_folder='web', static_url_path='')

#app.secret_key = 'your_secret_key'  # Set this to a random, secure value
app.secret_key = secrets.token_hex(16)

CONFIG_FILE = "config.json"
PASSWORD_FILE = 'password.json'
SESSION_COOKIE_NAME = 'session_id'
SESSIONS = {}
DEFAULT_PASSWORD_HASH = hashlib.sha256('hackme'.encode()).hexdigest()

def save_password(password_hash):
    with open(PASSWORD_FILE, 'w') as file: json.dump({'password': password_hash}, file)

def get_audio_devices():
    devices = sd.query_devices()
    output_devices = [device for device in devices if device['max_output_channels'] > 0]
    return [f"{device['name']}, {sd.query_hostapis()[device['hostapi']]['name']}" for device in output_devices]

def get_audio_inputs():
    devices = sd.query_devices()
    input_devices = [device for device in devices if device['max_input_channels'] > 0]
    return [f"{device['name']}, {sd.query_hostapis()[device['hostapi']]['name']}" for device in input_devices]

def list_tts_voices():
    try:
        try: pythoncom.CoInitialize()
        except: pass
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        return [voice.name for voice in voices]
    except Exception as e: print("[WEBSERVER]", e)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file: return json.load(file)
    except FileNotFoundError: return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file: json.dump(config, file, indent=4)

# Load the password from a file or use a default
def load_password():
    try:
        with open('password.json', 'r') as file:
            data = json.load(file)
            return data.get('password', DEFAULT_PASSWORD_HASH)
    except FileNotFoundError: return DEFAULT_PASSWORD_HASH

# Check if the user is authenticated
def is_authenticated():
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    return session_id in SESSIONS

# Create a new session
def create_session():
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    SESSIONS[session_id] = True
    return session_id

def GetActiveAlerts():
    try:
        with open("config.json", "r") as JCfile: config = JCfile.read()
        ConfigData = json.loads(config)
        ActiveAlerts = []
        HistoryFolder = "XMLhistory"
        XMLhistory = os.listdir(HistoryFolder)
        current_time = datetime.now(timezone.utc)
        for i in XMLhistory:
            try:
                with open(f"{HistoryFolder}/{i}", "r", encoding='utf-8') as f: XML = f.read()
                if "<InternalMonitor>SAME</InternalMonitor>" in XML:
                    Expires = datetime.fromisoformat(datetime.fromisoformat(re.search(r'<expires>\s*(.*?)\s*</expires>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)).astimezone(timezone.utc).isoformat())
                    if current_time > Expires:
                        try: os.remove(f"{HistoryFolder}/{i}")
                        except: pass
                        continue
                    
                    SourceHEADER = re.search(r'<SAME>\s*(.*?)\s*</SAME>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    MonitorName = re.search(r'<monitorName>\s*(.*?)\s*</monitorName>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    Sent = Sent.replace("T"," ")
                    expire = re.search(r'<expires>\s*(.*?)\s*</expires>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("T"," ")
                    txt = EAS2Text(SourceHEADER).EASText
                    ActiveAlerts.append(f"SAME from {MonitorName}\n Sent: {Sent}\n Expires: {expire}\n [{SourceHEADER}]\n\n {txt}")
                else:
                    Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    MessageType = re.search(r'<msgType>\s*(.*?)\s*</msgType>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    Status = re.search(r'<status>\s*(.*?)\s*</status>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    
                    XML = re.findall(r'<info>\s*(.*?)\s*</info>', XML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    InfoProc = 0
                    ExpireProc = 0
                    for InfoEN in XML:
                        InfoProc = InfoProc + 1
                        InfoEN = f"<info>{InfoEN}</info>"
                        try:
                            Expires = datetime.fromisoformat(datetime.fromisoformat(re.search(r'<expires>\s*(.*?)\s*</expires>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)).astimezone(timezone.utc).isoformat())
                            if current_time > Expires:
                                ExpireProc = ExpireProc + 1
                                continue
                        except:
                            ExpireProc = ExpireProc + 1
                            continue
                        
                        try:
                            if "fr" in re.search(r'<language>\s*(.*?)\s*</language>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1): lang = "fr"
                            elif "es" in re.search(r'<language>\s*(.*?)\s*</language>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1): lang = "es"
                            else: lang = "en"
                        except: lang = "en"
                        try:
                            if ConfigData[f'relay_{lang}'] is False: continue
                        except: continue

                        Urgency = re.search(r'<urgency>\s*(.*?)\s*</urgency>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        Severity = re.search(r'<severity>\s*(.*?)\s*</severity>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        Sent = Sent.replace("T"," ")
                        expire = re.search(r'<expires>\s*(.*?)\s*</expires>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("T"," ") 
                        senderName = re.search(r'<senderName>\s*(.*?)\s*</senderName>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        #ActiveAlerts.append(f"[CAP from {senderName}] [Sent: {Sent}] [Expires: {expire}] [{GeneratedHeader}]: {BroadcastText}")
                        Description = re.search(r'<description>\s*(.*?)\s*</description>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        event = re.search(r'<event>\s*(.*?)\s*</event>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        if Description == "###": continue
                        ActiveAlerts.append(f"CAP from {senderName}\n Sent: {Sent}\n Expires: {expire}\n{Status}, {MessageType}\n {Urgency}, {Severity}\n Event: {event}\n\n {Description}")
                    if InfoProc == ExpireProc:
                        try: os.remove(f"{HistoryFolder}/{i}")
                        except: pass
            except: continue
        return ActiveAlerts
    except: return []

# ... FLASK THINGS ...

@app.route('/activeAlerts')
def activeAlerts():
    try:
        ActiveAlerts = GetActiveAlerts()
        if not ActiveAlerts: return jsonify(["No alerts"])
        return jsonify(ActiveAlerts)
    except: return jsonify(["Error fetching alerts"])

@app.route('/config')
def config_page():
    if not is_authenticated(): return redirect(url_for('login_page'))
    
    return send_from_directory('web', 'config.html')
    #return send_from_directory('', 'config.html')

@app.route('/audio_devices')
def audio_devices():
    if not is_authenticated(): return jsonify({'error': 'Unauthorized'}), 401
    devices = get_audio_devices()
    return jsonify(devices)

@app.route('/audio_inputs')
def audio_inputs():
    if not is_authenticated(): return jsonify({'error': 'Unauthorized'}), 401
    devices = get_audio_inputs()
    return jsonify(devices)

@app.route('/tts_voices')
def tts_voices():
    if not is_authenticated(): return jsonify({'error': 'Unauthorized'}), 401
    voices = list_tts_voices()
    return jsonify(voices)

@app.route('/config_data')
def config_data():
    if not is_authenticated(): return jsonify({'error': 'Unauthorized'}), 401
    config = load_config()
    return jsonify(config)

@app.route('/save_config', methods=['POST'])
def save_config_data():
    if not is_authenticated(): return jsonify({'error': 'Unauthorized'}), 401
    config = request.json
    save_config(config)
    return 'Configuration saved successfully.', 200

@app.route('/change_password', methods=['POST'])
def change_password():
    if not is_authenticated(): return 'Unauthorized.', 401
    data = request.get_json()
    current_password_hash = hashlib.sha256(data['currentPassword'].encode()).hexdigest()
    new_password_hash = hashlib.sha256(data['newPassword'].encode()).hexdigest()
    if current_password_hash == load_password():
        save_password(new_password_hash)
        SESSIONS.clear() # Clear all sessions
        return 'Password changed successfully.', 200
    else: return 'Incorrect current password.', 403

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.json
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        if password_hash == load_password():
            session_id = create_session()
            response = make_response('Login successful.')
            response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True, samesite='Lax')
            return response
        else: return 'Incorrect password.', 403
    return send_from_directory('web', 'login.html')
    #return send_from_directory('', 'login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear all session data
    response = make_response(redirect('/login.html')) # Create a response object
    response.set_cookie(SESSION_COOKIE_NAME, '', expires=0) # Remove the session cookie
    return response

@app.route('/clearAlertLogTxt', methods=['POST'])
def clearAlertlogTxt():
    try:
        with open("alertlog.txt", "w") as f: f.write("")
    except: pass
    response = make_response(redirect('/alertLog.html'))
    return response

# Example mappings, replace with your actual mappings
#orgSAMEtoCAP = {'ORG1': 'Category1'}
#eventSAMEtoCAP = {'EVE1': 'Event1'}

@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.json
    nowTime = datetime.now(timezone.utc)
    sent = nowTime.strftime('%Y-%m-%dT%H:%M:%S-00:00')
    expire = nowTime + timedelta(hours=1)
    expire = expire.strftime('%Y-%m-%dT%H:%M:%S-00:00')
    sentforres = nowTime.strftime('%Y%m%dT%H%M%S')
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    res = f"{res}{sentforres}"

    try: Cate = orgSAMEtoCAP[data['ORG']]
    except: Cate = "Other"

    EVENT = data['EVE']
    EVENT = EVENT.upper()
    EVENT = EVENT[:3]

    finalXML = f"""
    <alert>
        <sender>QuantumENDECinternal</sender>
        <identifier>{res}</identifier>    
        <sent>{sent}</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <note>This file is NOT supposed to find its way to the Pelmorex NAADs system, it's impossibe for it to be there... if it's there, it's not supposed to be there.</note>
        <note>This is an QuantumENDEC internal alert</note> 

        <info>
            <language>en</language>
            <category>{Cate}</category>
            <event>internal</event>
            <urgency>Unknown</urgency>
            <severity>Unknown</severity>
            <certainty>Unknown</certainty>
            <expires>{expire}</expires>

            <eventCode>
                <valueName>SAME</valueName>
                <value>{EVENT}</value>
            </eventCode>
            
            <senderName>QuantumENDEC Internal</senderName>
            <headline>QuantumENDEC Internal CAP message</headline>
            <description>{data['broadcastText']}</description>
            
            <parameter>
                <valueName>layer:SOREM:1.0:Broadcast_Text</valueName>
                <value>{data['broadcastText']}</value>
            </parameter>

            <parameter>
                <valueName>EAS-ORG</valueName>
                <value>{data['ORG']}</value>
            </parameter>

            <area>
                <areaDesc>Specified Locations</areaDesc>
                <geocode>
                    <valueName>SAME</valueName>
                    <value>{data['FIPS']}</value>
                </geocode>
            </area>
        </info>
    </alert>
    """
    filenameXML = f"{sent.replace(':', '_')}I{res}.xml"
    print(f"Creating alert: {filenameXML}")
    with open(f"XMLqueue/{filenameXML}", "w") as file: file.write(finalXML)
    return 'Alert XML created successfully.'

@app.before_request
def require_login():
    if request.path not in ['/login', '/login.html', '/scroll.html', '/alert.txt', '/css/scrollStyle.css']:
        if not is_authenticated():
            return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        
        if password_hash == load_password():
            session_id = create_session()
            response = jsonify(message='Login successful.')
            response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True)
            return response
        else:
            return jsonify(message='Incorrect password.'), 403
    
    # Render login page if GET request
    return make_response(open('login.html').read())

@app.route('/upload_config', methods=['POST'])
def upload_config():
    SAVE_PATH = 'config.json'
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Only JSON files are accepted'}), 400

    file.save(SAVE_PATH)
    return jsonify({'success': 'File uploaded and saved as config.json'}), 200

@app.route('/upload_leadin', methods=['POST'])
def upload_leadin():
    SAVE_PATH = 'Audio/pre.wav'
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.wav'):
        return jsonify({'error': 'Only wav files are accepted'}), 400

    file.save(SAVE_PATH)
    return jsonify({'success': 'File uploaded and saved'}), 200

@app.route('/upload_leadout', methods=['POST'])
def upload_leadout():
    SAVE_PATH = 'Audio/post.wav'
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.wav'):
        return jsonify({'error': 'Only wav files are accepted'}), 400

    file.save(SAVE_PATH)
    return jsonify({'success': 'File uploaded and saved'}), 200

@app.route('/remove_Leadin', methods=['POST'])
def removeLeadin():
    try:
        os.remove("Audio/pre.wav")
        return jsonify({'success': 'Lead in audio removed'})
    except:
        return jsonify({'error': 'Failed to remove Lead in audio'})
    
@app.route('/remove_Leadout', methods=['POST'])
def removeLeadout():
    try:
        os.remove("Audio/post.wav")
        return jsonify({'success': 'Lead out audio removed'})
    except:
        return jsonify({'error': 'Failed to remove Lead out audio'})

@app.route('/')
def home():
    return send_from_directory('web', 'index.html')
    #return make_response(open('index.html').read())

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/<path:path>')
def static_files(path):
    # Serve HTML files from the 'web' folder
    if path.endswith('.html'):
        return send_from_directory('web', path)
    # Serve static files (CSS, JS, images) from the same directory as the Flask script
    return send_from_directory('', path)
    #return send_from_directory('', path)


import logging

def StartWEB(HOST, PORT):
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host=HOST, port=PORT, debug=False)

if __name__ == '__main__':
    PORT = 8050
    StartWEB("0.0.0.0", PORT)
