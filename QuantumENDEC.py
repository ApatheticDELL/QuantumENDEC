import threading, os, time
#QUANTUMENDEC LAUNCH FILE

print("QuantumENDEC")
print("Version 3: The Clean Up")
print("")
print("Devloped by...")
print("Dell ... ApatheticDELL")
print("Aaron ... secludedcfox.com :3")
print("BunnyTub ... gadielisawesome")

time.sleep(3)

try:
    os.remove("SameHistory.txt")
except:
    with open("SameHistory.txt", "a") as f:
        f.write(f"ZXZX-STARTER-\n")
    f.close()

dir = 'XMLhistory'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

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