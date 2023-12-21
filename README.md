ApatheticDELL presents...
# QuantumENDEC (v3.4.0)

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
QuantumENDEC: The Future of ENDECs.

### Install (SECTION INCOMPLETE)
Installing the QuantumENDEC is quite easy.
You will first require the following...
- FFMPEG
- Python3 (install pip3 too)
...to be installed on your System

It is advised to use the latest version of Python!

Then install the Python modules required using pip:
```pip3 install -r requirements.txt```

(Soon we will set up a batch and bash script to install everything...)

### Setup
The alert audio will play on your default sound device, whether it be on Linux or Windows.

Before doing anything, you need to have some knowledge on the Canadian public alerting system... more precisely, Pelmorex and its CAP-CP XML files.
You can read about it on this PDF from Pelmorex: https://alerts.pelmorex.com/wp-content/uploads/2021/06/NAADS-LMD-User-Guide-R10.0.pdf

Go into the config.json file to configure the software.
You'll find discord webhook settings, along with filters for alert statuses, severity, and urgency.

There's also some Experimental Settings with audio, but, best to leave them be since mostly they're for the future.

After you're done configuring, start QuantumENDEC by just running...
```python3 QuantumENDEC.py```

NOTE!!
In the audio folder, attn.wav is static! Try not to remove it.
You can add pre.wav and/or post.wav in the Audio folder.

Everything should work on its own!

### Some Extra Additional Information
This software ENDEC will NOT work with American CAP alerts, since it's designed for the CAP Canadian Profile. Also, the way it grabs alerts is different from FEMA CAP, in Canada, there is one centralized internet TCP feed that ENDECs across Canada connect to. The system is designed by Pelmorex.

If you see anything about matches or match files, it just means that the software already processed the thing/file in question.

Finally, even though this was coded from (mostly) the ground up, I'd still like to credit libmarleu's BashENDEC (which no longer exists on their page) for starting out the QuantumENDEC journey all the way in 2021...

And thanks to all who worked on this one, hell of an ENDEC...
