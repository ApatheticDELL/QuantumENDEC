ApatheticDELL presents...
# QDEC v5

## Credits
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

## Description
QDEC is a Emergency Alerting Software. It has the ability to grab alerts from Canadian CAP, American CAP, and SAME.

(Previously known as QuantumENDEC)

## Install
Installing the QDEC is quite easy.

> [!CAUTION]
> QDEC must be run on a system with one or more audio output devices. It will most likely not function in an online environment, thus, issues with QDEC inside of online environments such as github.dev may be ignored and closed.

### Required software
You will also require the following software...
- [Python](https://www.python.org/) (At least 3.13+)
- [FFmpeg](https://ffmpeg.org/)

### Optional software
- [multimon-ng](https://github.com/EliasOenal/multimon-ng) If you are using any of the SAME monitor functions with QDEC on linux: You need to install multimon-ng. (The Multimon-NG binary for windows is included with QDEC.)
- [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version) (If you are going to use map generation on Windows)
...to be installed

### Software for TTS generation
Not all of them needs to be installed. You can choose what TTS service you want to use in the QDEC web interface.
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng) (Windows and Linux.)
- [Piper](https://github.com/rhasspy/piper) (Windows and Linux.)
- [flite](https://github.com/festvox/flite) (Linux. You MAY be able to use it on Windows if you can find a Windows binary and add it to the PATH)
- [Maki](https://bunnytub.com/Maki.html) (Windows only.)

#### Some things to account for
- Note, that eSpeak NG is selected by default.
- To use Piper with QDEC in Windows and Linux, you must place the Piper folder with it's binary within the root of the QDEC folder.
- Piper voices and their JSON must be placed in a folder called piper_voices in the root of the QDEC folder.
- Maki is Windows only, and it's binary is already included. Maki allows the use of 32-bit and 64-bit TTS voices on Windows.
- ElevenLabs voices uses a python module, you may already have it if you installed all the python modules from (requirements.txt)

### Required python modules
All the required Python modules are in the 'requirements.txt' text file.

## Setup
Before doing anything, you need to have some knowledge of the Canadian public alerting system... more precisely, Pelmorex and its CAP-CP XML files.
You can read about it on this PDF from Pelmorex: https://alerts.pelmorex.com/wp-content/uploads/2021/06/NAADS-LMD-User-Guide-R10.0.pdf
You may not need this if you are just using QDEC with S.A.M.E audio monitors.

Just run ```py QDEC.py``` or whatever to run the main QDEC.py script to start QDEC and the web interface server.
The python command may be different depending on your python installation... (it could be py, or python3)

QDEC will already be running.
The web interface server by default will be running on port 8050, to access, simply open a web browser and go to http://localhost:5000 or http://{ip_of_device}:5000
You can change this in the configuration section of the web interface server, or in the config.json file.

The default password to access the web interface server is ```hackme```
The first thing you should do is change that default password, it's just asking people to hack your QDEC web interface.

You can change the password in the "Change Access Password" tab in the QDEC web interface.
Make sure you press the "Change Password" button to set your passwords.

After you changed your password, you will want to go into the "Configuration" tab on the web interface and set up QDEC.
You'll find discord webhook settings, along with filters for alert statuses, severity, and urgency.
You can filter alerts via CAP-CP Geocodes and S.A.M.E CLC (Canada's FIPS), you can filter by provinice and/or region.

NOTE!!
By default, all capture/monitor sources will be disabled by default. You will need to activate them in the Configuration tab.
Also, some settings will require a restart of QDEC to take effect.

Filter by province example...
SAME CLC: 04 for Ontario. (Don't put 040000 unless you want to exclude its sub-regions) 
CAP-CP Geocode: 35* for Ontario.

Filter by region example...
SAME CLC: 0466 for Halton - Peel, Ontario. (Don't put 046600 unless you want to exclude its sub-regions)
CAP-CP Geocode: 3521 for just Peel Region, Ontario or 3521* for Peel region and anything else in there.

And then you can still use the full code to be very spicific in both CAP-CP Geocodes and SAME CLC. You'll still need to know the codes... here are some resources for finding location codes.
(For SAME CLC (Canada's FIPS)): https://en.wikipedia.org/wiki/Forecast_region
(For CAP-CP Geocodes): https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/capcp-lctn-rfrncs/index4-en.aspx (Scroll down and you'll find a link to the Excel file containing all the location codes for CAP-CP)

After you're done configuring, make sure you save your changes by pressing "Save" on the bottom of the page.

The web interface has the ability to load the current configuration when you access the page.

You can run QDEC with arguments, run it with "-h" for more info.

Everything should work on its own!

If you see anything about matches or match files, it just means that the software already processed the thing/file in question.

## Additional Information

Emergency information does come from official resources (by default, unless changed), though one shouldn't fully rely on QDEC itself for emergency information as errors could still occur

Finally, even though this was coded from (mostly) the ground up, I'd still like to credit Libmarleu's BashENDEC (which no longer exists on their page) for starting the QDEC journey in 2021...

And thanks to all who worked on this one, hell of an ENDEC...
