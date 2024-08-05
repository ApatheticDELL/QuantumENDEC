from EAS2Text import EAS2Text
from datetime import datetime, timezone, timedelta
import random, string, subprocess, sys, threading, queue, os, wave, contextlib, base64, json, time, ffmpeg, requests
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from scipy.fft import *
from scipy.io import wavfile
import numpy
assert numpy
from logger import Log

def UpdateStatus(service, content):
    try:
        statFolder = "stats"
        with open(f"{statFolder}/{service}_status.txt", "w") as f: f.write(content)
    except: pass

def createXML(SAME, audioInput, XMLfolder, monitorName):
    try:
        XMLfolder = XMLfolder.replace("/","")
        sent = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S-00:00')
        ident = f"{sent.replace("-","").replace(":","")}{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"
        output = f"{XMLfolder}/{monitorName}-{sent.replace("-","_").replace(":","_")}I{ident}.xml"
        current_time = datetime.strptime(sent, "%Y-%m-%dT%H:%M:%S-00:00")
        try:
            oof = EAS2Text(SAME)
            hours, minutes = map(int, oof.purge)
        except: hours, minutes = map(int, ['01','30'])
        expiry_time = current_time + timedelta(hours=hours, minutes=minutes)
        expiry_timestamp = expiry_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")
        with open(audioInput, 'rb') as wav_file: wav_data = wav_file.read()
        encoded_data = base64.b64encode(wav_data).decode('utf-8')

        XML = f"""
        <alert>
            <InternalMonitor>SAME</InternalMonitor>
            <monitorName>{monitorName}</monitorName>
            <note>This is QuantumENDEC's AmericanMode alert</note>
            <identifier>{ident}</identifier>
            <sent>{sent}</sent>
            <expires>{expiry_timestamp}</expires>
            <SAME>{SAME}</SAME>
            <BroadcastAudio>
                <mimeType>audio/wav</mimeType>
                <AudioBASE64>
                    {encoded_data}
                </AudioBASE64>
            </BroadcastAudio>
        </alert>
        """

        with open(output, "w") as f: f.write(XML)
        print(f"[{monitorName}]: XML creation success")
    except: print(f"[{monitorName}]: XML creation failed.")

def setup(moniName):
    print(f"[Setup][{moniName}]  Using Default Audio Input...")
    print(f"[Setup][{moniName}]  Cleaning Up Old Files...")
    files = os.listdir('Audio/tmp')
    files_to_del = [f"{moniName}-out.wav", f"{moniName}-rmend0.wav", f"{moniName}-alert.wav"]
    for name in files:
        if name in files_to_del: os.remove(f"Audio/tmp/" + name)
    if sys.platform == "win32": platform = "win"
    else: platform = "other"
    return platform

def clr_dir(moniName):
    files = os.listdir('Audio/tmp')
    for name in files:
        #Make sure to not delete the output (alert)
        if name != f"{moniName}-alert.wav" and moniName in name: os.remove(f"Audio/tmp/" + f"{name}")
    print(f"[{moniName}] Cleaned Up tmp Directory")

def get_len(fname):
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

def freq(file, start_time, end_time):
    sr, data = wavfile.read(file)
    if data.ndim > 1: data = data[:, 0]
    else: pass
    dataToRead = data[int(start_time * sr / 1000) : int(end_time * sr / 1000) + 1]
    N = len(dataToRead)
    yf = rfft(dataToRead)
    xf = rfftfreq(N, 1 / sr)
    # Get the most dominant frequency and return it
    idx = numpy.argmax(numpy.abs(yf))
    freq = xf[idx]
    return freq

def RemoveEOMpATTN(moniName):
    moniName = f"{moniName}-"
    try:
        # Remove END (EOMs)
        audio = AudioSegment.from_file(f"Audio/tmp/{moniName}out.wav")
        lengthaudio = len(audio)
        start = 0
        threshold = lengthaudio - 1200
        end = 0
        counter = 0
        end += threshold
        chunk = audio[start:end]
        filename = f'Audio/tmp/{moniName}rmend{counter}.wav'
        chunk.export(filename, format="wav")
        counter +=1
        start += threshold
        print(f"[{moniName}] Removed Recording EOMs")
    except: print(f"[{moniName}] Failed to remove recording EOMs")
    
    try:
        # Remove attention tone
        timelist = []
        freqlist = []
        ATTNCUT = 0
        file_length = get_len(f"Audio/tmp/{moniName}rmend0.wav")
        if file_length < 23: file_length = round(file_length)
        else: file_length = 80
        cnt = 0
        for e in range(file_length):
            cnt = cnt + 1
            val = 300
            start = e * val
            offset = start + val
            timelist.append(start)
            frequency = freq(f"Audio/tmp/{moniName}rmend0.wav", start, offset)
            freqlist.append(frequency)
        freqlist = list(freqlist)
        mainlen = len(freqlist)
        found = False
        for e in range(len(freqlist)):
            if found == False:
                if 810 < round(int(freqlist[e])) < 1070:
                    if 810 < round(int(freqlist[e + 1])) < 1070 and 810 < round(int(freqlist[e + 2])) < 1070:
                        found = True
            elif found == True:
                if freqlist[e] < 810 or freqlist[e] > 1070:
                    if e + 5 < mainlen:
                        if freqlist[e + 1] < 810 or freqlist[e + 1] > 1070 and freqlist[e + 2] < 810 or freqlist[e + 2] > 1070 and freqlist[e + 3] < 810 or freqlist[e + 3] > 1070 and freqlist[e + 4] < 810 or freqlist[e + 4] > 1070 and freqlist[e + 5] < 810 or freqlist[e + 5] > 1070:
                            end_point = e
                            found = None
        filename = f"Audio/tmp/{moniName}alert.wav"
        if(found == None):
            audio = AudioSegment.from_file(f"Audio/tmp/{moniName}rmend0.wav")
            lengthaudio = len(audio)
            cut = 300 * end_point
            start = cut
            threshold = lengthaudio - cut
            end = lengthaudio
            counter = 0
            while start < len(audio):
                end += threshold
                chunk = audio[start:end]
                chunk.export(filename, format="wav")
                counter +=1
                start += threshold
        else:
            gl = round(get_len(f"Audio/tmp/{moniName}rmend0.wav"))
            if(gl > 4): end_point = 17 #5 seconds
            else: end_point = gl // 2
            audio = AudioSegment.from_file(f"Audio/tmp/{moniName}rmend0.wav")
            lengthaudio = len(audio)
            cut = 300 * end_point
            start = cut
            threshold = lengthaudio - cut
            end = lengthaudio
            counter = 0
            while start < len(audio):
                end += threshold
                chunk = audio[start:end]
                chunk.export(filename, format="wav")
                counter +=1
                start += threshold
        print(f"[{moniName}] Removed ATTN Tone")
    except: print(f"[{moniName}] Failed to remove ATTN Tone")

def ZCZC_test(inp):
    inp = inp.split("-")
    num = len(inp) - 6
    if len(inp[num + 3]) != 7: return False
    elif len(inp[num + 4]) != 8: return False
    elif len(inp[0]) != 4: return False #ZCZC
    elif len(inp[1]) != 3: return False #"EAS"
    elif len(inp[2]) != 3: return False #"DMO"
    if num == 1 and len(inp[3]) == 11: return True
    elif num > 1:
        for e in range(num):
            if (e + 1) == num:
                if len(inp[e+3]) == 11: return True
                else: return False
            elif len(inp[e+3]) != 6: return False
    else: return False

class AUDIODEVmonitor:
    def __init__(self, monitorName):
        self.monitorName = monitorName
        self.record = False

    def recordAUDIO(self, SAME):
        while True:
            sd.default.reset()
            samplerate = 8000
            file = f"Audio/tmp/{self.monitorName}-out.wav"
            q = queue.Queue()

            def callback(indata, frames, time, status):
                if status: print(status, file=sys.stderr)
                q.put(indata.copy())

            with sf.SoundFile(file, mode='x', samplerate=samplerate,channels=2) as file:
                with sd.InputStream(samplerate=samplerate,channels=2,callback=callback):
                    print(f"[{self.monitorName}] Recording!")
                    last_check_time = time.time()
                    while True:
                        file.write(q.get())
                        current_time = time.time()
                        if self.record is False or current_time - last_check_time > 120:
                            file.close()
                            print(f"[{self.monitorName}] Stopped Recording Thread")
                            RemoveEOMpATTN(self.monitorName)
                            clr_dir(self.monitorName)
                            createXML(SAME, f"Audio/tmp/{self.monitorName}-alert.wav", "XMLqueue", self.monitorName)
                            UpdateStatus(self.monitorName, f"Alert sent.")
                            print(f"[{self.monitorName}]  Alert Sent!\n\n")
                            exit()

    def start(self):
        while True:
            try:
                platform = setup(self.monitorName)
                last = None
                if platform == "win": source_process = subprocess.Popen(["multimon-ng-WIN32/multimon-ng.exe", "-a", "EAS", "-q"], stdout=subprocess.PIPE)
                else: source_process = subprocess.Popen(["multimon-ng", "-a", "EAS", "-q"], stdout=subprocess.PIPE)
                UpdateStatus(self.monitorName, f"Ready For Alerts.")
                print(f"[{self.monitorName}]  Ready For Alerts...\n")

                while True:
                    line = source_process.stdout.readline().decode("utf-8")
                    decode = line.replace("b'EAS: ", "").replace("\n'", "").replace("'bEnabled Demodulators: EAS", "").replace('EAS:  ', '').replace('EAS: ', '').replace('Enabled demodulators: EAS', '')
                    if "ZCZC-" in decode or "NNNN" in decode: print(f"[{self.monitorName}]  Decoder: {decode}")

                    if 'ZCZC-' in str(line):
                        if ZCZC_test(decode) == True:
                            SAME = decode.replace("\n", "")
                            UpdateStatus(self.monitorName, f"Receiving alert...")
                            print(f"[{self.monitorName}] ZCZC Check OK")
                            with open("config.json", "r") as JCfile: config = JCfile.read()
                            ConfigData = json.loads(config)
                            logge = Log(ConfigData)
                            dateNow = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
                            logge.SendLog("Emergency Alert Received", f"Receipt: Received on {dateNow} from {self.monitorName}", SAME)
                            self.record = True
                            RecordThread = threading.Thread(target = self.recordAUDIO, args=(decode,))
                            RecordThread.start()
                        else:
                            print(f"[{self.monitorName}] WARNING: ZCZC Check FAILED!")
                            line = "NNNN"
                    
                    elif 'NNNN' not in str(last):
                        if 'NNNN' in str(line):
                            self.record = False
                            try: RecordThread.join()
                            except: pass
                            UpdateStatus(self.monitorName, f"Ready For Alerts.")
                    last = line
            except Exception as e:
                UpdateStatus(self.monitorName, f"Failure")
                print(f"[{self.monitorName}] Monitor failure.", e)
                time.sleep(20)


class IPmonitor:
    def __init__(self, monitorName, streamURL):
        self.monitorName = monitorName
        self.streamURL = streamURL
        self.record = False

    def is_stream_online(self):
        try:
            response = requests.get(self.streamURL, stream=True, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"[{self.monitorName}] Error checking stream URL: {e}")
            return False
    
    def RecordIP(self, ZCZC):
        output_file = f"Audio/tmp/{self.monitorName}-out.wav"
        RecordIP = (ffmpeg .input(self.streamURL) .output(output_file, format='wav', ar='8000') .run_async(pipe_stdout=True, pipe_stderr=True))
        seconds = 0
        while True:
            seconds = seconds + 1
            if self.record is False or seconds == 120 or seconds > 120:
                RecordIP.terminate()
                RecordIP.wait()
                # try: shutil.copy(f"Audio/tmp/{self.monitorName}-out.wav", f"{self.monitorName}_alertFullish.wav")
                # except: pass
                print(f"[{self.monitorName}] Stopped Recording Thread")
                RemoveEOMpATTN(self.monitorName)
                clr_dir(self.monitorName)
                createXML(ZCZC, f"Audio/tmp/{self.monitorName}-alert.wav", "XMLqueue", self.monitorName)
                UpdateStatus(self.monitorName, f"Alert sent.")
                print(f"[{self.monitorName}]  Alert Sent!\n\n")
                exit()
            time.sleep(1)

    def decodeStream(self):
        try:
            # Command to capture audio from IP stream and pipe it to multimon-ng
            ffmpeg_command = [
                'ffmpeg', 
                '-i', self.streamURL,         # Input stream URL
                '-f', 'wav',              # Output format
                '-ac', '1',              # Number of audio channels (1 for mono)
                '-ar', '22050',          # Audio sample rate
                '-loglevel', 'quiet',    # Suppress ffmpeg output
                '-' ]

            platform = setup(self.monitorName)
            last = None
            ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
            platform = "win"
            if platform == "win": source_process = subprocess.Popen(['multimon-ng-WIN32/multimon-ng.exe', '-a', 'EAS', '-q', '-t', 'raw', '-'], stdin=ffmpeg_process.stdout, stdout=subprocess.PIPE)
            else: source_process = subprocess.Popen(['multimon-ng', '-a', 'EAS', '-q', '-t', 'raw', '-'], stdin=ffmpeg_process.stdout, stdout=subprocess.PIPE)
            UpdateStatus(self.monitorName, f"Ready For Alerts, listening to {self.streamURL}")
            print(f"[{self.monitorName}]  Ready For Alerts, listening to {self.streamURL}\n")

            while True:
                line = source_process.stdout.readline().decode("utf-8")
                decode = line.replace("b'EAS: ", "").replace("\n'", "").replace("'bEnabled Demodulators: EAS", "").replace('EAS:  ', '').replace('EAS: ', '').replace('Enabled demodulators: EAS', '')
                if "ZCZC-" in decode or "NNNN" in decode: print(f"[{self.monitorName}]  Decoder: {decode}")

                if 'ZCZC-' in str(line):
                    if ZCZC_test(decode) == True:
                        SAME = decode.replace("\n", "")
                        UpdateStatus(self.monitorName, f"Receiving alert...")
                        print(f"[{self.monitorName}] ZCZC Check OK")
                        with open("config.json", "r") as JCfile: config = JCfile.read()
                        ConfigData = json.loads(config)
                        logge = Log(ConfigData)
                        dateNow = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
                        logge.SendLog("Emergency Alert Received", f"Receipt: Received on {dateNow} from {self.monitorName}", decode)
                        self.record = True
                        RecordThread = threading.Thread(target = self.RecordIP, args=(decode,))
                        RecordThread.start()
                    else:
                        print(f"[{self.monitorName}] WARNING: ZCZC Check FAILED!")
                        line = "NNNN"
                
                elif 'NNNN' not in str(last):
                    if 'NNNN' in str(line):
                        time.sleep(0.5)
                        self.record = False
                        try: RecordThread.join()
                        except: pass
                        UpdateStatus(self.monitorName, f"Ready For Alerts, listening to {self.streamURL}")
                last = line
        except:
            try:
                ffmpeg_process.terminate()
                source_process.terminate()
            except: pass
            UpdateStatus(self.monitorName, f"Failure")
            print(f"[{self.monitorName}] Monitor failure.")
            time.sleep(20)

    def start(self):
        while True:
            if self.is_stream_online() is False:
                print(f"[{self.monitorName}] Stream URL {self.streamURL} is offline or unreachable.")
                UpdateStatus(self.monitorName, f"Stream URL {self.streamURL} is offline or unreachable.")
            else:
                try:
                    decodeThread = threading.Thread(target=self.decodeStream)
                    decodeThread.daemon = True
                    decodeThread.start()
                    while True:
                        time.sleep(30)
                        if self.is_stream_online() is False:
                            print(f"[{self.monitorName}] Stream URL {self.streamURL} is offline or unreachable.")
                            UpdateStatus(self.monitorName, f"Stream URL {self.streamURL} is offline or unreachable.")
                            time.sleep(30)
                            break
                        else: pass
                except:
                    print(f"[{self.monitorName}] Monitor failure.")
                    UpdateStatus(self.monitorName, f"Failure.")
            time.sleep(30)

def IPmonitor_run(name, url):
    i = IPmonitor(name, url)
    i.start()

def AUDIOmonitor_run(name):
    i = AUDIODEVmonitor(name)
    i.start()

if __name__ == "__main__":
    
    
    exit()
    result = IPmonitor("test", "https://icecast.kodicable.net:8443/wcrf").is_stream_online()
    print(result)
    
    print("testing only")
    moni = "Test"

    #AudioMonitor = AUDIODEVmonitor(moni).start()
    #AudioMonitor

    # Replace with your IP stream URL
    # self.streamURL = "https://archive.secludedfox.com/comcast/getfile.php?v=3zE6dEocEe-_fbwkEa-VhA=="
    # self.streamURL = 'https://icecast.wxstream.org/IP/CWXV'
    streamURL = "http://192.168.2.36:8000/TEST"
    monitorName = "TestMonitorIP"

    IPmonitor(monitorName, streamURL).start()
    #StreamMonitor = 
    #StreamMonitor.start()