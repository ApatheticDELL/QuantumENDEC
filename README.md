ApatheticDELL presents...
# QuantumENDEC (v5 Public Beta 4)

### Credits
Developed by...
```
Dell ... ApatheticDELL
Aaron ... secludedfox.com
BunnyTub ... bunnytub.com
```

Assisted by...
```
AC ... AC5230
ChatGPT ... chat.openai.com
```

### Description
QuantumENDEC is a Canadian CAP Emergency Alerting Software. Its primary goal is to encode Canadian Emergency Alerts into S.A.M.E alerts!

### Install
Installing the QuantumENDEC is quite easy.
You will first require the following...
- FFMPEG
- Python (3+)
...to be installed on your System

And then, you need the following required Python modules: EASGen, EAS2Text, discord_webhook, pyttsx3, sounddevice, numpy, scipy, requests, argparse, xmltodict, pydub, ffmpeg-python, flask, soundfile

If running on windows: You may also need pythoncom

If you are using any of the SAME monitor functions with QuantumENDEC on linux: You need to install multimon-ng.
The Multimon-NG binary for windows is included with QuantumENDEC.

### Setup
Before doing anything, you need to have some knowledge of the Canadian public alerting system... more precisely, Pelmorex and its CAP-CP XML files.
You can read about it on this PDF from Pelmorex: https://alerts.pelmorex.com/wp-content/uploads/2021/06/NAADS-LMD-User-Guide-R10.0.pdf

Just run ```python QuantumENDEC.py``` to start QuantumENDEC and the web interface server.
The python command may be different depending on your python installation... (it could be py, or python3)

QuantumENDEC will already be running.
The web interface server by default will be running on port 8050, to access, simply open a web browser and go to http://localhost:8050 or http://{ip_of_device}:8050
You can change this in the configuration section of the web interface server, or in the config.json file.

The default password to access the web interface server is ```hackme```
The first thing you should do is change that default password, it's just asking people to hack your QuantumENDEC web interface.

You can change the password in the "Change Access Password" tab in the QuantumENDEC web interface.
Make sure you press the "Change Password" button to set your passwords.

After you changed your password, you will want to go into the "Configuration" tab on the web interface and set up QuantumENDEC.
You'll find discord webhook settings, along with filters for alert statuses, severity, and urgency.
You can filter alerts via CAP-CP Geocodes and S.A.M.E CLC (Canada's FIPS), you can filter by provinice and/or region.

NOTE!!
By default, all capture/monitor sources will be disabled by default. You will need to activate them in the Configuration tab.
Also, some settings will require a restart of QuantumENDEC to take effect.

Filter by province example...
SAME CLC: 04 for Ontario. (Don't put 040000 unless you want to exclude its sub-regions) 
CAP-CP Geocode: 35 for Ontario.

Filter by region example...
SAME CLC: 0466 for Halton - Peel, Ontario. (Don't put 046600 unless you want to exclude its sub-regions)
CAP-CP Geocode: 3521 for Peel Region, Ontario

And then you can still use the full code to be very spicific in both CAP-CP Geocodes and SAME CLC. You'll still need to know the codes... here are some resources for finding location codes.
(For SAME CLC (Canada's FIPS)): https://en.wikipedia.org/wiki/Forecast_region
(For CAP-CP Geocodes): https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/capcp-lctn-rfrncs/index4-en.aspx (Scroll down and you'll find a link to the Excel file containing all the location codes for CAP-CP)

After you're done configuring, make sure you save your changes by pressing "Save" on the bottom of the page.

The web interface has the ability to load the current configuration when you access the page, except for the discord webhook color (you're going to need to keep setting the discord webhook color every time you make a change.)

You can run QuantumENDEC with arguments, run it with "-h" for more info.

NOTE!!
In the audio folder, the attention tones are static! Try not to remove/change it. (Unless you know what you're doing)
You can add pre.wav and/or post.wav in the Audio folder. (Or do it in the web interface (Home tab, there is the button to manage lead in/out audio))

Everything should work on its own!

### Some Extra Additional Information
~~This software ENDEC will NOT work with American CAP alerts, since it's designed for the CAP Canadian Profile. Also, the way it grabs alerts is different from FEMA CAP, in Canada, there is one centralized internet TCP feed that ENDECs across Canada connect to. The system is designed by Pelmorex.~~ ... About that...

If you see anything about matches or match files, it just means that the software already processed the thing/file in question.

Emergency information does come from official resources (by default, unless changed), though one shouldn't fully rely on QuantumENDEC itself for emergency information as errors could still occur

Finally, even though this was coded from (mostly) the ground up, I'd still like to credit Libmarleu's BashENDEC (which no longer exists on their page) for starting the QuantumENDEC journey in 2021...

And thanks to all who worked on this one, hell of an ENDEC...