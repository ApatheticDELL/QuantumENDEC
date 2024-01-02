import threading, os, time
#QUANTUMENDEC LAUNCH FILE
version = "v3.4.2"

print(f"""
QuantumENDEC ({version})

Developed by...
Dell ... ApatheticDELL
Aaron ... secludedfox.com :3
BunnyTub ... gadielisawesome
""")

time.sleep(3)

try:
    os.remove("SameHistory.txt")
except:
    with open("SameHistory.txt", "a") as f:
        f.write(f"ZXZX-STARTER-\n")
    f.close()

#Clears folders
def ClearFolder(dir):
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
ClearFolder('XMLhistory')
ClearFolder('XMLprocess')
ClearFolder('XMLqueue')

# start capture.py and relay.py and loop them
def startRelay():
    while True:
        os.system("python3 relay.py")
        time.sleep(0.1)

def startCapture():
    while True:
        os.system("python3 capture.py")
        time.sleep(0.1)

captureThread = threading.Thread(target=startCapture)
relayThread = threading.Thread(target=startRelay)

captureThread.start()
relayThread.start()

'''
while True:
    time.sleep(100)
    # dont ask just keeps the file alive
'''

print("File end")
exit()
