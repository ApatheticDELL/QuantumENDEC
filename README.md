ApatheticDELL presents...
# QuantumENDEC (v4.4.1)

### Credits
Developed by...
```
Dell ... ApatheticDELL
Aaron ... secludedfox.com
BunnyTub ... gadielisawesome
```

Assisted by...
```
AC ... AC5230
ChatGPT ... chat.openai.com
```

### Description
QuantumENDEC is a Canadian CAP Emergency Alerting Software. Its primary goal is to encode Canadian Emergency Alerts into S.A.M.E alerts!

### Install (SECTION INCOMPLETE)
Installing the QuantumENDEC is quite easy.
You will first require the following...
- FFMPEG
- Python3
...to be installed on your System

And then, you need the following required Python modules: EASGen, EAS2Text, discord_webhook, pyttsx3, sounddevice, numpy, scipy, requests, argparse, xmltodict, pydub, pygame.

### Setup
Before doing anything, you need to have some knowledge of the Canadian public alerting system... more precisely, Pelmorex and its CAP-CP XML files.
You can read about it on this PDF from Pelmorex: https://alerts.pelmorex.com/wp-content/uploads/2021/06/NAADS-LMD-User-Guide-R10.0.pdf

You need to set a config file before doing anything.
There is a config.json file that is used to configure the software.
You can create one by running: ```python SetupQE.py```
You'll find discord webhook settings, along with filters for alert statuses, severity, and urgency.
You will also be asked if you want to filter alerts via CAP-CP Geocodes and S.A.M.E CLC (Canada's FIPS), you can filter by provinice and/or region.

To filter by province...
SAME CLC: 04 for Ontario. (Don't put 040000 unless you want to exclude its sub-regions) 
CAP-CP Geocode: 35 for Ontario.

To filter by region...
SAME CLC: 0466 for Halton - Peel, Ontario. (Don't put 046600 unless you want to exclude its sub-regions)
CAP-CP Geocode: 3521 for Peel Region, Ontario

And then you can still use the full code to be very spicific in both CAP-CP Geocodes and SAME CLC. You'll still need to know the codes... here are some resources for finding location codes.
(For SAME CLC (Canada's FIPS)): https://en.wikipedia.org/wiki/Forecast_region
(For CAP-CP Geocodes): https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/capcp-lctn-rfrncs/index4-en.aspx (Scroll down and you'll find a link to the Excel file containing all the location codes for CAP-CP)

After you're done configuring, start QuantumENDEC by just running...
```python QuantumENDEC.py```

You can run QuantumENDEC with arguments, run it with "-h" for more info.

NOTE!!
In the audio folder, attn.wav is static! Try not to remove it.
You can add pre.wav and/or post.wav in the Audio folder.

Everything should work on its own!

### Some Extra Additional Information
This software ENDEC will NOT work with American CAP alerts, since it's designed for the CAP Canadian Profile. Also, the way it grabs alerts is different from FEMA CAP, in Canada, there is one centralized internet TCP feed that ENDECs across Canada connect to. The system is designed by Pelmorex.

You can run QuantumENDEC with arguments now...
```python QuantumENDEC.py -h```
For more information.

If you see anything about matches or match files, it just means that the software already processed the thing/file in question.

Emergency information does come from official resources, though one shouldn't fully rely on QE for emergency information as errors could still occur

Finally, even though this was coded from (mostly) the ground up, I'd still like to credit Libmarleu's BashENDEC (which no longer exists on their page) for starting the QuantumENDEC journey in 2021...

And thanks to all who worked on this one, hell of an ENDEC...