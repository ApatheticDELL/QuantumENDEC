#!/usr/bin/env python3

# QuantumENDEC v5
# Devloped by ApatheticDELL alongside Aaron and BunnyTub

# IMPORTS
import os
import sys
import json
import shutil
import time
import requests
import threading
import re
import xmltodict
import socket
import base64
import contextlib
import random
import string
import wave
import ffmpeg
import subprocess
import queue
import argparse
import hashlib
import secrets
import logging
import signal
import pyttsx3
import importlib.util

import numpy
assert numpy

import sounddevice as sd
import soundfile as sf

#from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime, timezone, timedelta
from EAS2Text import EAS2Text
from EASGen import EASGen
from urllib.request import Request, urlopen
from pydub import AudioSegment
from scipy.io import wavfile
from scipy.fft import *
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, make_response, session

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DiscordWebhook_available = True
try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
except Exception as e:
    print("[ATTENTION]: Discord Webhook will not be available!", e)
    DiscordWebhook_available = False

elevenlabs_available = True
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
except Exception as e:
    print("[ATTENTION]: ElevenLabs TTS will not be available!", e)
    elevenlabs_available = False

mapGeneration_available = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import cartopy.io.shapereader as shpreader
    from matplotlib.patches import Polygon
    from matplotlib.lines import Line2D
except Exception as e:
    print("[ATTENTION]: Map generation will not be available!", e)
    mapGeneration_available = False

# UNIVERSAL VARS
QuantumENDEC_Version = "v5source"
assets_folder = "./assets"
history_folder = "./history"
queue_folder = "./queue"
tmp_folder = f"{assets_folder}/tmp"

PlayoutAlerts = True
global_qe_status = 0

# GENERAL FUNCTIONS
def get_platform():
    """ 'win' or 'other' """
    if sys.platform == "win32": platform = "win"
    else: platform = "other"
    return platform

if get_platform() == "win": import pythoncom

def get_cap_value(data={}, key="valueName", value=""):
    """ will return None if not found """
    if isinstance(data, dict): data = [data]
    for item in data:
        if item.get(key) == value:
            return item
    return None

def write_file(content, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

def append_file(content, filename):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(content)

def read_file(filename):
    with open(filename, "r", encoding='utf-8') as file:
        content = file.read()
    return content

def delete_file(filename):
    os.remove(filename)

def list_folder(folder):
    folder_list = os.listdir(folder)
    return folder_list

def copy_file(file_in, file_out):
    shutil.copy(file_in, file_out)

def move_file(file_in, file_out):
    shutil.move(file_in, file_out)

def run_plugins(mode=None, ZCZC="", broadcast_text="", alert_xml="", info_dict={}):
    """ Modes: on_start, before_relay, after_relay """
    plugins_folder = "./plugins"
    ZCZC = str(ZCZC).replace("\n", "")
    broadcast_text = str(broadcast_text).replace("\n", " ")
    alert_xml = str(alert_xml).replace("\n", " ")

    if os.path.exists(plugins_folder) and mode is not None:
        print("Attempting to run plugins...")
        plugin_list = os.listdir(plugins_folder)

        for plugin_file in plugin_list:
            if plugin_file.endswith(".py"):
                plugin_name = plugin_file[:-3]
                plugin_path = os.path.join(plugins_folder, plugin_file)

                try:
                    print(f"Running plugin: {plugin_name}")
                    
                    # Load the module from file
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Call the appropriate function based on mode
                    if mode == "before_relay" and hasattr(module, "ExecutePlugin_BeforeRelay"):
                        module.ExecutePlugin_BeforeRelay(ZCZC, broadcast_text, alert_xml, info_dict)
                    elif mode == "after_relay" and hasattr(module, "ExecutePlugin_AfterRelay"):
                        module.ExecutePlugin_AfterRelay(ZCZC, broadcast_text, alert_xml, info_dict)
                    elif mode == "on_start" and hasattr(module, "ExecutePlugin_OnStart"):
                        module.ExecutePlugin_OnStart()

                except Exception as e:
                    print(f"Plugin '{plugin_name}' failed to run. Error: {e}")

def log_alert(content):
    output = "./assets/alertlog.txt"
    content = content + "\n\n"
    try: append_file(content, output)
    except: write_file(content, output)

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        config = file.read()
    CONFIG_DATA = json.loads(config)
    return CONFIG_DATA

def write_json(filename, new_data={}):
    with open(filename, 'w', encoding="utf-8") as file:
        json.dump(new_data, file, indent=4)

def qe_status(mode="read", new_data=0):
    """ 'set' or 'read' the status of QuantumENDEC. 0=Normal, 1=Restart, 2=Shutdown. """
    new_data = int(new_data)
    mode = str(mode)
    mode = mode.lower()
    global global_qe_status
    if mode == "read": return global_qe_status
    elif mode == "set": global_qe_status = new_data

def set_status(name, description=""):
    write_file(description, f"./stats/{name}_status.txt")

def update_cgen(headline="EAS DETAILS", text="", background_color="000000", text_color="ffffff", alert_status=True):
    cgen_j = {
        "headline":headline,
        "text":text,
        "background_color":background_color,
        "text_color":text_color,
        "alert_status":alert_status
    }
    write_json("./assets/cgen.json", cgen_j)
    print("Updated CGEN. Showing:", alert_status)

def get_audio_outputs():
    devices = sd.query_devices()
    output_devices = [device for device in devices if device['max_output_channels'] > 0]
    return_devices = []
    for device in output_devices:
        dev_name = (f"{device['name']} {sd.query_hostapis()[device['hostapi']]['name']}")
        dev_id = device['index']
        return_devices.append(f"{dev_id}, {dev_name}")
    return return_devices

def list_tts_voices():
    try:
        try: pythoncom.CoInitialize()
        except: pass
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        listed_voices = []
        for voice in voices:
            voice_id = voice.id
            voice_id = voice_id.replace("\\", "/")
            listed_voices.append(voice.name)
        engine.stop()
        return listed_voices
    except Exception as e:
        print("[Webserver]: Exception getting the list of TTS voices (pyttsx3): ", e)
        try: engine.stop()
        except: pass
        return []

cap2same_org = { "Met": "WXR", "Admin": "EAS", "Other": "CIV", }

same2cap_org = { "WXR":"Met", "EAS":"Admin", "CIV":"Other" }

cap2same_event = {
    "911Service": "TOE",
    "accident": "CDW",
    "admin":"ADR",
    "aircraftCras":"LAE",
    "airportClose":"ADR",
    "airQuality":"SPS",
    "airspaceClos":"ADR",
    "amber":"CAE",
    "ambulance":"LAE",
    "animalDang":"CDW",
    "animalDiseas":"CDW",
    "animalFeed":"CEM",
    "animalHealth":"CEM",
    "arcticOut":"SVS",
    "avalanche":"AVW",
    "aviation":"LAE",
    "biological":"BHW",
    "blizzard":"BZW",
    "bloodSupply":"LAE",
    "blowingSnow":"WSW",
    "bridgeClose":"LAE",
    "cable":"ADR",
    "chemical":"CHW",
    "civil":"CEM",
    "civilEmerg":"CEM",
    "civilEvent":"CEM",
    "cold":"SVS",
    "coldWave":"SVS",
    "crime":"CDW",
    "damBreach":"DBW",
    "damOverflow":"DBW",
    "dangerPerson":"CDW",
    "diesel":"LAE",
    "drinkingWate":"CWW",
    "dustStorm":"DSW",
    "earthquake":"EQW",
    "electric":"POS",
    "emergFacil":"CEM",
    "emergSupport":"CEM",
    "explosive":"HMW",
    "facility":"CEM",
    "fallObject":"HMW",
    "fire":"FRW",
    "flashFlood":"FFW",
    "flashFreeze":"FSW",
    "flood":"FLW",
    "fog":"SPS",
    "foodSupply":"LAE",
    "forestFire":"WFW",
    "freezeDrzl":"WSW",
    "freezeRain":"WSW",
    "freezngSpray":"WSW",
    "frost":"SPS",
    "galeWind":"HWW",
    "gasoline":"LAE",
    "geophyiscal":"CEM",
    "hazmat":"BHW",
    "health":"BHW",
    "heat":"SVS",
    "heatHumidity":"SVS",
    "heatingOil":"LAE",
    "heatWave":"SVS",
    "highWater":"SVS",
    "homeCrime":"CEM",
    "hospital":"LAE",
    "hurricane":"HUW",
    "hurricFrcWnd":"HUW",
    "ice":"SPS",
    "iceberg":"IBW",
    "icePressure":"SPS",
    "industCrime":"CEM",
    "industryFire":"IFW",
    "infectious":"DEW",
    "internet":"ADR",
    "lahar":"VOW",
    "landslide":"LSW",
    "lavaFlow":"VOW",
    "magnetStorm":"CDW",
    "marine":"SMW",
    "marineSecure":"SMW",
    "meteor":"CDW",
    "missingPer":"MEP",
    "missingVPer":"MEP",
    "naturalGas":"LAE",
    "nautical":"ADR",
    "notam":"ADR",
    "other":"CEM",
    "overflood":"FLW",
    "plant":"LAE",
    "plantInfect":"LAE",
    "product":"LAE",
    "publicServic":"LAE",
    "pyroclasFlow":"VOW",
    "pyroclaSurge":"VOW",
    "radiological":"RHW",
    "railway":"LAE",
    "rainfall":"SPS",
    "rdCondition":"LAE",
    "reminder":"CEM",
    "rescue":"CEM",
    "retailCrime":"CEM",
    "road":"LAE",
    "roadClose":"ADR",
    "roadDelay":"ADR",
    "roadUsage":"ADR",
    "rpdCloseLead":"ADR",
    "satellite":"ADR",
    "schoolBus":"ADR",
    "schoolClose":"ADR",
    "schoolLock":"CDW",
    "sewer":"LAE",
    "silver":"CEM",
    "snowfall":"WSW",
    "snowSquall":"WSW",
    "spclIce":"SPS",
    "spclMarine":"SMW",
    "squall":"SMW",
    "storm":"SVS",
    "stormFrcWnd":"SVS",
    "stormSurge":"SSW",
    "strongWind":"HWW",
    "telephone":"LAE",
    "temperature":"SPS",
    "terrorism":"CDW",
    "testMessage":"DMO",
    "thunderstorm":"SVR",
    "tornado":"TOR",
    "traffic":"ADR",
    "train":"ADR",
    "transit":"ADR",
    "tropStorm":"TRW",
    "tsunami":"TSW",
    "urbanFire":"FRW",
    "utility":"ADR",
    "vehicleCrime":"CEM",
    "volcanicAsh":"VOW",
    "volcano":"VOW",
    "volunteer":"ADR",
    "waste":"ADR",
    "water":"ADR",
    "waterspout":"SMW",
    "weather":"SPS",
    "wildFire":"FRW",
    "wind":"HWW",
    "windchill":"SPS",
    "winterStorm":"WSW"
}

# types (in values): text, bool, list
valid_configs = {
    "webserver_host":"text",
    "webserver_port":"text",
    "relay_en":"bool",
    "relay_fr":"bool",
    "force_120":"bool",
    "produce_alertimage":"bool",
    "attn_tone":"text",
    "attn_basedoncountry":"bool",
    "enable_leadin":"bool",
    "enable_leadout":"bool",
    "SAME":"bool",
    "SAME_callsign":"text",
    "SAME_filterORG":"list",
    "SAME_filterEVE":"list",
    "SAME_filterFIPS":"list",
    "SAME_blockEVE":"list",
    "CGEN_clear_after_relay":"bool",
    "CGEN_warningcolor_background":"text",
    "CGEN_warningcolor_text":"text",
    "CGEN_watchcolor_background":"text",
    "CGEN_watchcolor_text":"text",
    "CGEN_advisorycolor_background":"text",
    "CGEN_advisorycolor_text":"text",
    "enable_plugins":"bool",
    "use_specifiedaudiooutput":"bool",
    "specifiedaudiooutput":"list",
    "use_audiodevice_id":"bool",
    #"use_defaultTTS":"bool",
    #"TTS_en":"text",
    #"TTS_fr":"text",

    "tts_service": "text",
    "pyttsx3_defaultTTS": "bool",
    "pyttsx3_en": "text",
    "pyttsx3_fr": "text",
    "maki_en": "text",
    "maki_fr": "text",
    "ElevenLabs_apiKey": "text",
    "ElevenLabs_voiceID_en": "text",
    "ElevenLabs_modelID_en": "text",
    "ElevenLabs_voiceID_fr": "text",
    "ElevenLabs_modelID_fr": "text",

    "discordwebhook_enable": "bool",
    "discordwebhook_author_name": "text",
    "discordwebhook_author_URL": "text",
    "discordwebhook_author_iconURL": "text",
    "discordwebhook_URL": "text",
    "discordwebhook_sendAudio": "bool",
    "discordwebhook_sendImage": "bool",
    "email_enable": "bool",
    "email_user": "text",
    "email_userPassword": "text",
    "email_SMTPserver": "text",
    "email_SMTPport": "text",
    "email_recipients": "text",
    "statusTest": "bool",
    "statusActual": "bool",
    "messagetypeAlert": "bool",
    "messagetypeUpdate": "bool",
    "messagetypeCancel": "bool",
    "messagetypeTest": "bool",
    "severityExtreme": "bool",
    "severitySevere": "bool",
    "severityModerate": "bool",
    "severityMinor": "bool",
    "severityUnknown": "bool",
    "urgencyImmediate": "bool",
    "urgencyExpected": "bool",
    "urgencyFuture": "bool",
    "urgencyPast": "bool",
    "urgencyUnknown": "bool",
    "CAPCP_geocodefilter":"list",
    "TCP_CAP": "bool",
    "TCP_CAP_ADDR1": "text",
    "TCP_CAP_ADDR2": "text",
    "HTTP_CAP": "bool",
    "HTTP_CAP_ADDR1": "text",
    "HTTP_CAP_ADDR2": "text",
    "HTTP_CAP_ADDR3": "text",
    "HTTP_CAP_ADDR4": "text",
    "HTTP_CAP_ADDR5": "text",
    "NWS_CAP": "bool",
    "NWS_CAP_AtomLink": "text",
    "SAME_AudioDevice_Monitor": "bool",
    "SAME_AudioStream_Monitor": "bool",
    "SAME_AudioStream_Monitor1": "text",
    "SAME_AudioStream_Monitor2": "text",
    "SAME_AudioStream_Monitor3": "text",
    "SAME_AudioStream_Monitor4": "text"
}

default_config = {
    "quantumendec_version":f"{QuantumENDEC_Version}",
    "webserver_host":"0.0.0.0",
    "webserver_port":"80",
    "relay_en":True,
    "relay_fr":False,
    "force_120":True,
    "produce_alertimage":False,
    "attn_tone":"AttnRumble.wav",
    "attn_basedoncountry":False,
    "enable_leadin":True,
    "enable_leadout":True,
    "SAME":False,
    "SAME_callsign":"QUANTUM0",
    "SAME_filterORG":[],
    "SAME_filterEVE":[],
    "SAME_filterFIPS":[],
    "SAME_blockEVE":[],
    "CGEN_clear_after_relay": True,
    "CGEN_warningcolor_background":"ff2a2a",
    "CGEN_warningcolor_text":"ffffff",
    "CGEN_watchcolor_background":"ffcc00",
    "CGEN_watchcolor_text":"000000",
    "CGEN_advisorycolor_background":"00aa00",
    "CGEN_advisorycolor_text":"ffffff",
    "enable_plugins":False,
    "use_specifiedaudiooutput":False,
    "specifiedaudiooutput":[],
    "use_audiodevice_id": False,
    #"use_defaultTTS":True,
    #"TTS_en":"",
    #"TTS_fr":"",
    "tts_service": "pyttsx3",
    "pyttsx3_defaultTTS": True,
    "pyttsx3_en": "",
    "pyttsx3_fr": "",
    "maki_en": "",
    "maki_fr": "",
    "ElevenLabs_apiKey": "",
    "ElevenLabs_voiceID_en": "",
    "ElevenLabs_modelID_en": "",
    "ElevenLabs_voiceID_fr": "",
    "ElevenLabs_modelID_fr": "",
    "discordwebhook_enable": False,
    "discordwebhook_author_name": "",
    "discordwebhook_author_URL": "",
    "discordwebhook_author_iconURL": "",
    "discordwebhook_URL": "",
    "discordwebhook_sendAudio": False,
    "discordwebhook_sendImage": False,
    "email_enable": False,
    "email_user": "",
    "email_userPassword": "",
    "email_SMTPserver": "",
    "email_SMTPport": "",
    "email_recipients": "",
    "statusTest": True,
    "statusActual": True,
    "messagetypeAlert": True,
    "messagetypeUpdate": True,
    "messagetypeCancel": True,
    "messagetypeTest": True,
    "severityExtreme": True,
    "severitySevere": True,
    "severityModerate": True,
    "severityMinor": True,
    "severityUnknown": True,
    "urgencyImmediate": True,
    "urgencyExpected": True,
    "urgencyFuture": True,
    "urgencyPast": True,
    "urgencyUnknown": True,
    "CAPCP_geocodefilter":[],
    "TCP_CAP": False,
    "TCP_CAP_ADDR1": "streaming1.naad-adna.pelmorex.com:8080",
    "TCP_CAP_ADDR2": "streaming2.naad-adna.pelmorex.com:8080",
    "HTTP_CAP": False,
    "HTTP_CAP_ADDR1": "",
    "HTTP_CAP_ADDR2": "",
    "HTTP_CAP_ADDR3": "",
    "HTTP_CAP_ADDR4": "",
    "HTTP_CAP_ADDR5": "",
    "NWS_CAP": False,
    "NWS_CAP_AtomLink": "https://api.weather.gov/alerts/active.atom",
    "SAME_AudioDevice_Monitor": False,
    "SAME_AudioStream_Monitor": False,
    "SAME_AudioStream_Monitor1": "",
    "SAME_AudioStream_Monitor2": "",
    "SAME_AudioStream_Monitor3": "",
    "SAME_AudioStream_Monitor4": ""
}

def get_alert_colors(ConfigData, ZCZC=None):
    """ returns: dict of 'background_color' and 'text_color' """
    colEvtlist = {
        "AVA": 1,
        "CFA": 1,
        "FFA": 1,
        "FLA": 1,
        "HUA": 1,
        "HWA": 1,
        "SSA": 1,
        "SVA": 1,
        "TOA": 1,
        "TRA": 1,
        "TSA": 1,
        "WSA": 1,
        "DBA": 1,
        "EVA": 1,
        "WFA": 1,
        "AVW": 0,
        "BLU": 0,
        "BZW": 0,
        "CDW": 0,
        "CEM": 0,
        "CFW": 0,
        "DSW": 0,
        "EAN": 0,
        "EQW": 0,
        "EVI": 0,
        "EWW": 0,
        "FFW": 0,
        "FLW": 0,
        "FRW": 0,
        "FSW": 0,
        "FZW": 0,
        "HMW": 0,
        "HUW": 0,
        "HWW": 0,
        "LEW": 0,
        "NUW": 0,
        "RHW": 0,
        "SMW": 0,
        "SPW": 0,
        "SQW": 0,
        "SSW": 0,
        "SVR": 0,
        "TOR": 0,
        "TRW": 0,
        "TSW": 0,
        "VOW": 0,
        "WSW": 0,
        "BHW": 0,
        "BWW": 0,
        "CHW": 0,
        "CWW": 0,
        "DBW": 0,
        "DEW": 0,
        "FCW": 0,
        "IBW": 0,
        "IFW": 0,
        "LSW": 0,
        "WFW": 0,
        "MEP": 0
    }

    if ZCZC is not None:
        try:
            ZCZC = ZCZC.split("-")
            evnt = ZCZC[2]
            if evnt in colEvtlist:
                if colEvtlist[evnt] == 0:
                    background_color = ConfigData["CGEN_warningcolor_background"]
                    text_color = ConfigData["CGEN_warningcolor_text"]
                elif colEvtlist[evnt] == 1:
                    background_color = ConfigData["CGEN_watchcolor_background"]
                    text_color = ConfigData["CGEN_watchcolor_text"]
            else:
                background_color = ConfigData["CGEN_advisorycolor_background"]
                text_color = ConfigData["CGEN_advisorycolor_text"]
        except:
            background_color = ConfigData["CGEN_warningcolor_background"]
            text_color = ConfigData["CGEN_warningcolor_text"]
    else:
        background_color = ConfigData["CGEN_warningcolor_background"]
        text_color = ConfigData["CGEN_warningcolor_text"]
    
    return { "background_color":background_color, "text_color":text_color }

def watch_notify(queue_folder="./queue", history_folder="./history"):
    print(f"Waiting for an alert...")
    while True:
        if qe_status() != 0:
            return None

        queue_list = list_folder(queue_folder)
        for file in queue_list:
            with open(f"{queue_folder}/{file}", "r", encoding='UTF-8') as f: RelayXML = f.read()
            AlertListXML = re.findall(r'<alert\s*(.*?)\s*</alert>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if len(AlertListXML) > 1:
                print("WHY THE F*** IS THERE 2 ALERT ELEMENTS IN A SINGLE XML FILE?!!?")
                delete_file(f"{queue_folder}/{file}")
                AlertCount = 0
                for AlertXML in AlertListXML:
                    AlertCount = AlertCount + 1
                    Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', AlertXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_").replace("\n", "")
                    Ident = re.search(r'<identifier>\s*(.*?)\s*</identifier>', AlertXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_").replace("\n", "")
                    NAADsFilename = f"{Sent}I{Ident}.xml"
                    AlertXML = f"<alert {AlertXML}</alert>"
                    with open(f"{queue_folder}/{NAADsFilename}", 'w', encoding='utf-8') as f: f.write(AlertXML)
            
            elif file in list_folder(history_folder):
                print("No relay: watch folder files matched.")
                delete_file(f"{queue_folder}/{file}")
            
            else:
                return f"{file}"

        time.sleep(1)

def filter_check_CAP(config_data={}, info_dict={}):
    # Returns True if passed
    Urgency = info_dict.get("urgency")
    Severity = info_dict.get("severity")
    Expires = info_dict.get("expires", None)

    try:
        current_time = datetime.now(timezone.utc)
        Expires = datetime.fromisoformat(datetime.fromisoformat(Expires).astimezone(timezone.utc).isoformat())
        if current_time > Expires: Expired = True
        else: Expired = False
    except: Expired = False
    
    parameter = info_dict.get("parameter")
    if parameter is not None:
        Broadcast_Immediately = "no"
        x = get_cap_value(parameter, "valueName", "layer:SOREM:1.0:Broadcast_Immediately")
        if x is not None: Broadcast_Immediately = str(x.get("value"))
        if "yes" in Broadcast_Immediately.lower(): Broadcast_Immediately = True
        else: Broadcast_Immediately = False
    else: Broadcast_Immediately = False

    # To check the 'CAP-CP Geocodes' - not for FIPS/CLC
    if len(config_data['CAPCP_geocodefilter']) == 0: GecodeResult = True
    else:
        GeocodeList = []
        areas = info_dict.get("area")
        for area in areas:
            geocodes = area.get("geocode")
            x = get_cap_value(geocodes, "valueName", "profile:CAP-CP:Location:0.3")
            if x is not None:
                GeocodeList.append(str(x.get("value")))
        GecodeResult = False
        if not (len(GeocodeList) == 0):
            for i in GeocodeList:
                if i[:2] in config_data['CAPCP_geocodefilter']: GecodeResult = True
                if i[:3] in config_data['CAPCP_geocodefilter']: GecodeResult = True
                if i[:4] in config_data['CAPCP_geocodefilter']: GecodeResult = True
                if i in config_data['CAPCP_geocodefilter']: GecodeResult = True
        else: GecodeResult = True

    Language = info_dict.get("language")
    if Language is not None:
        Language = Language.lower()
        if "fr-ca" in Language: Language = "fr"
        elif "en-ca" in Language or "en-us" in Language: Language = "en"
        else: Language = "NOT_SUPPORTED"
        Language_Result = config_data.get(f"relay_{Language}", False)
    else: Language_Result = False

    print("<< Filter Check (CAP) >>")
    print("Severity: ", config_data[f"severity{Severity}"])
    print("Urgency: ", config_data[f"urgency{Urgency}"])
    print("Broadcat Immedately (CAP-CP only): ", Broadcast_Immediately)
    print("Geocode result (CAP-CP only): ", GecodeResult)
    print("Language result: ", Language_Result)
    print("Expired: ", Expired)
    if ((config_data[f"severity{Severity}"] and config_data[f"urgency{Urgency}"]) or Broadcast_Immediately) and GecodeResult and Language_Result and not Expired: print("Final result: Pass")
    else: print("Final result: Failed... alert will be skipped.")

    return ((config_data[f"severity{Severity}"] and config_data[f"urgency{Urgency}"]) or Broadcast_Immediately) and GecodeResult and Language_Result and not Expired

def filter_check_SAME(ConfigData, ZCZC=""):
    """Returns True if the filter matches alert"""
    SAME_OOF = EAS2Text(str(ZCZC))
    EVENT = SAME_OOF.evnt
    ORGINATOR = SAME_OOF.org
    LOCATIONS = SAME_OOF.FIPS
    
    if "EAN" in EVENT or "NIC" in EVENT or "NPT" in EVENT or "RMT" in EVENT or "RWT" in EVENT:
        EventAllowed = True
    else:
        if len(ConfigData['SAME_filterEVE']) == 0: EventAllowed = True
        else:
            if EVENT in ConfigData['SAME_filterEVE']: EventAllowed = True
            else: EventAllowed = False
        
        if EVENT in ConfigData['SAME_blockEVE']: EventAllowed = False

    if len(ConfigData['SAME_filterORG']) == 0: OrgiResult = True
    else:
        if ORGINATOR in ConfigData['SAME_filterORG']: OrgiResult = True
        else: OrgiResult = False

    if len(ConfigData['SAME_filterFIPS']) == 0: LocationResult = True
    else:
        LocationResult = False
        for i in LOCATIONS:
            # Partial county wildcard filter
            partial = "*" + i[1:]
            if partial[:2] in ConfigData['SAME_filterFIPS']: LocationResult = True
            if partial[:3] in ConfigData['SAME_filterFIPS']: LocationResult = True
            if partial[:4] in ConfigData['SAME_filterFIPS']: LocationResult = True
            if partial in ConfigData['SAME_filterFIPS']: LocationResult = True

            if i[:2] in ConfigData['SAME_filterFIPS']: LocationResult = True
            if i[:3] in ConfigData['SAME_filterFIPS']: LocationResult = True
            if i[:4] in ConfigData['SAME_filterFIPS']: LocationResult = True
            if i in ConfigData['SAME_filterFIPS']: LocationResult = True

    print("<< Filter check (S.A.M.E) >>")
    print("Originator result: ", OrgiResult)
    print("Location code result: ", LocationResult)
    print("Event code allowed: ", EventAllowed)
    if (OrgiResult and LocationResult and EventAllowed): print("Final result: pass")
    else: print("Final result: fail... alert will be skipped.")

    return (OrgiResult and LocationResult and EventAllowed)

def get_alert_region(AlertDICT):
    # Get the alert region of CAP XML
    codes = AlertDICT.get("code")
    if codes is None: return None
    if isinstance(codes, dict): codes = [codes]
    if "profile:CAP-CP:0.4" in str(codes): CODE = "CANADA"
    elif "IPAWSv1.0" in str(codes): CODE = "USA"
    else: CODE = None
    return CODE
    
def check_folder(dir, Clear=False):
    if not os.path.exists(dir): os.makedirs(dir)
    else:
        if Clear is True:
            for f in os.listdir(dir): os.remove(os.path.join(dir, f))

def grab_geotoclc():
    # this fixes that ugly code that i said aaron would cringe at
    geo_to_clc_file = f"./{assets_folder}/GeoToCLC.csv"
    csv_contents = read_file(geo_to_clc_file)
    csv_dict = {}
    for line in csv_contents.strip().splitlines():
        parts = line.split(",")
        if len(parts) >= 2:
            key = parts[0].strip()
            value = parts[1].strip()
            csv_dict[key] = value
    return csv_dict

def process_heartbeat(References, QueueFolder, HistoryFolder):
    print("[NAADS HEARTBEAT PROCESSOR]: Downloading (Pelmorex NAADs) alerts from received heartbeat...")
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
        Output = f"{QueueFolder}/{sent}I{identifier}.xml"
        if f"{sent}I{identifier}.xml" in os.listdir(f"{HistoryFolder}"):
            print("[NAADS HEARTBEAT PROCESSOR]: Heartbeat, no download: Files matched.")
        else:
            print(f"[NAADS HEARTBEAT PROCESSOR]: Downloading: {sent}I{identifier}.xml...")
            req1 = Request(url = f'http://{Dom1}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
            req2 = Request(url = f'http://{Dom2}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
            try: xml = urlopen(req1).read()
            except:
                try: xml = urlopen(req2).read()
                except: pass
            try:
                with open(Output, "wb") as f: f.write(xml)
            except: print("[NAADS HEARTBEAT PROCESSOR]: Heartbeat, download aborted: a general exception occurred, it could be that the URLs are temporarily unavailable.")

def get_media(input_source, media_output, decode_type):
    if decode_type == "base64":
        print("Decoding media from BASE64...")
        with open(media_output, "wb") as fh: fh.write(base64.decodebytes(input_source))
    elif decode_type == "url_download":
        print("Downloading media...")
        r = requests.get(input_source)
        with open(media_output, 'wb') as f: f.write(r.content)

def trim_audio(input_file, max_duration_ms=120000):
    # For broadcast audio
    output_file = input_file + ".trimmed"
    audio = AudioSegment.from_file(input_file)
    duration_ms = len(audio)
    if duration_ms > max_duration_ms:
        trimmed_audio = audio[:max_duration_ms]
        trimmed_audio.export(output_file, format="wav")
        print(f"Broadcast Audio trimmed to {max_duration_ms / 1000} seconds.")
        move_file(output_file, input_file)
    else: pass

def convert_media(inputAudio, outputAudio):
    """ uses ffmpeg to convert media """
    result = subprocess.run(["ffmpeg", "-y", "-i", inputAudio, outputAudio], capture_output=True, text=True)
    if result.returncode == 0: print(f"{inputAudio} --> {outputAudio} ... Conversion successful!")
    else: print(f"{inputAudio} --> {outputAudio} ... Conversion failed: {result.stderr}")

# The functions for the audio monitors
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
    idx = numpy.argmax(numpy.abs(yf)) # Get the most dominant frequency and return it
    freq = xf[idx]
    return freq

def Remove_EOMandATTN(AudioFile):
    try:
        # Remove END (EOMs)
        # audio = AudioSegment.from_file(f"Audio/tmp/{moniName}out.wav")
        audio = AudioSegment.from_file(AudioFile)
        lengthaudio = len(audio)
        start = 0
        threshold = lengthaudio - 1200
        end = 0
        counter = 0
        end += threshold
        chunk = audio[start:end]
        filename = f"{AudioFile}.rmend"
        chunk.export(filename, format="wav")
        counter +=1
        start += threshold
    except: pass
    
    try:
        # Remove attention tone
        timelist = []
        freqlist = []
        ATTNCUT = 0
        file_length = get_len(f"{AudioFile}.rmend")
        if file_length < 23: file_length = round(file_length)
        else: file_length = 80
        cnt = 0
        for e in range(file_length):
            cnt = cnt + 1
            val = 300
            start = e * val
            offset = start + val
            timelist.append(start)
            frequency = freq(f"{AudioFile}.rmend", start, offset)
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
        if(found == None): pass
        else:
            gl = round(get_len(f"{AudioFile}.rmend"))
            if(gl > 4): end_point = 17 #5 seconds
            else: end_point = gl // 2
        audio = AudioSegment.from_file(f"{AudioFile}.rmend")
        lengthaudio = len(audio)
        cut = 300 * end_point
        start = cut
        threshold = lengthaudio - cut
        end = lengthaudio
        counter = 0
        move_file(AudioFile, f"{AudioFile}.backup")
        while start < len(audio):
            end += threshold
            chunk = audio[start:end]
            chunk.export(AudioFile, format="wav")
            counter +=1
            start += threshold
        delete_file(f"{AudioFile}.backup")
    except Exception as e:
        print("Error in removing the attention tone: ", e)
        try: move_file(f"{AudioFile}.backup", AudioFile)
        except: pass

def CreateXML_from_MonitorSAME(SAME, audioInput, monitorName):
    try:
        SAME = SAME.replace("\n", "")
        oof = EAS2Text(SAME)
        sent = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S-00:00')
        sent_rp = sent.replace("-","").replace(":","")
        ident_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        ident = f"{sent_rp}{ident_code}"
        output = f"{queue_folder}/{monitorName}-{sent_rp}I{ident}.xml"
        current_time = datetime.strptime(sent, "%Y-%m-%dT%H:%M:%S-00:00")
        Headline = f"{oof.orgText} has issued {oof.evntText}".replace("\n", "")
        
        try: hours, minutes = map(int, oof.purge)
        except: hours, minutes = map(int, ['01','30'])
        expiry_time = current_time + timedelta(hours=hours, minutes=minutes)
        expiry_timestamp = expiry_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")
        
        monitorName = monitorName.replace("\n", "")
        try: Cate = same2cap_org[oof.org]
        except: Cate = "Other"
        FIPs = "-".join(oof.FIPS)

        try:
            with open(audioInput, 'rb') as wav_file: wav_data = wav_file.read()
            encoded_data = base64.b64encode(wav_data).decode('utf-8')
            embedded_audio = f"""
            <resource>
                <resourceDesc>broadcast audio</resourceDesc>
                <mimeType>audio/wave</mimeType>
                <derefUri>{encoded_data}</derefUri>
            </resource>
            """
        except: embedded_audio = ""

        XML = f"""
        <alert>
            <identifier>{ident}</identifier>
            <sender>{monitorName}</sender>
            <sent>{sent}</sent>
            <status>Actual</status>
            <msgType>Alert</msgType>
            <source>QuantumENDEC Internal Monitor</source>
            <scope>Public</scope>
            <info>
                <language>en-US</language>
                <category>{Cate}</category>
                <event>{oof.evnt}</event>
                <responseType>Monitor</responseType>
                <urgency>Immediate</urgency>
                <severity>Extreme</severity>
                <certainty>Observed</certainty>
                <eventCode><valueName>SAME</valueName><value>{oof.evnt}</value></eventCode>
                <effective>{sent}</effective>
                <expires>{expiry_timestamp}</expires>
                <senderName>{oof.orgText}</senderName>
                <headline>{Headline}</headline>
                <description>Starting at {oof.startTimeText}, ending at {oof.endTimeText}. ({oof.callsign})</description>
                {embedded_audio}
                <parameter><valueName>EAS-ORG</valueName><value>{oof.org}</value></parameter>
                <area><areaDesc>{oof.strFIPS}</areaDesc><geocode><valueName>SAME</valueName><value>{FIPs}</value></geocode></area>
            </info>
        </alert>
        """
        write_file(XML, output)
    except: pass

# CLASSES
class Webserver:
    def __init__(self, HOST="0.0.0.0", PORT="80"):
        try:
            if int(PORT) > 65535: PORT = "80"
            if int(PORT) < 0: PORT = "80"
        except: PORT = "80"
        
        self.HOST = HOST
        self.PORT = PORT
        self.QEWEB_flaskapp = Flask(__name__)
        self.setup_routes()
        self.QEWEB_flaskapp.secret_key = secrets.token_hex(16)
        self.PASSWORD_FILE = './password.json'
        self.SESSION_COOKIE_NAME = 'session_id'
        self.SESSIONS = {}
        self.DEFAULT_PASSWORD_HASH = hashlib.sha256('hackme'.encode()).hexdigest()

    def save_password(self, password_hash):
        with open(self.PASSWORD_FILE, 'w') as file: json.dump({'password': password_hash}, file)
    
    # Check if the user is authenticated
    def is_authenticated(self):
        session_id = request.cookies.get(self.SESSION_COOKIE_NAME)
        return session_id in self.SESSIONS
    
    # Load the password from a file or use a default
    def load_password(self):
        try:
            with open('password.json', 'r') as file:
                data = json.load(file)
                return data.get('password', self.DEFAULT_PASSWORD_HASH)
        except FileNotFoundError: return self.DEFAULT_PASSWORD_HASH

    # Create a new session
    def create_session(self):
        session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.SESSIONS[session_id] = True
        return session_id
    
    def get_active_alerts(self):
        try:
            ConfigData = load_json(f"{assets_folder}/config.json")
            ActiveAlerts = []
            XMLhistory = list_folder(history_folder)
            current_time = datetime.now(timezone.utc)
            for i in XMLhistory:
                try:
                    XML = read_file(f"{history_folder}/{i}")
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
                        Description = re.search(r'<description>\s*(.*?)\s*</description>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        event = re.search(r'<event>\s*(.*?)\s*</event>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        if Description == "###": continue
                        ActiveAlerts.append(f"CAP from {senderName}\n Sent: {Sent}\n Expires: {expire}\n{Status}, {MessageType}\n {Urgency}, {Severity}\n Event: {event}\n\n {Description}")
                    if InfoProc == ExpireProc:
                        try: delete_file(f"{history_folder}/{i}")
                        except: pass
                except: continue
            return ActiveAlerts
        except: return ["Something went wrong getting alerts"]

    def setup_routes(self):
        @self.QEWEB_flaskapp.route('/activeAlerts')
        def activeAlerts():
            try:
                ActiveAlerts = self.get_active_alerts()
                if not ActiveAlerts: return jsonify(["No alerts"])
                return jsonify(ActiveAlerts)
            except: return jsonify(["Error fetching alerts"])

        @self.QEWEB_flaskapp.route('/statuses')
        def get_stats():
            if not self.is_authenticated(): return jsonify({'error': 'Unauthorized'}), 401
            status_dict = {}
            x = list_folder("./stats")
            for i in x:
                y = read_file(f"./stats/{i}")
                i = i.replace(".txt", "")
                status_dict[i] = y
            return jsonify(status_dict)
        
        @self.QEWEB_flaskapp.route('/alert_log')
        def alert_log():
            try:
                x = read_file(f"{assets_folder}/alertlog.txt")
                if x == "": x = "There's nothing here!"
            except: x = "There's nothing here!"
            return x
        
        @self.QEWEB_flaskapp.route('/clearAlertLogTxt', methods=['POST'])
        def clearAlertlogTxt():
            write_file("", f"{assets_folder}/alertlog.txt")
            response = make_response(redirect('/alertLog.html'))
            return response
        
        @self.QEWEB_flaskapp.route('/version')
        def GetVersion():
            return QuantumENDEC_Version
        
        @self.QEWEB_flaskapp.route('/restart', methods=['GET'])
        def RestartQE():
            if qe_status() == 1:
                return "QuantumENDEC is already in the process of restarting!"

            if qe_status() == 2:
                return "QuantumENDEC is already in the process of shutting down!"
            
            if qe_status() == 0:
                qe_status("set", 1)
                return "Now restarting QuantumENDEC... Check the status tab for QuantumENDEC's condition. The restart may take a while."
        
        @self.QEWEB_flaskapp.route('/shutdown', methods=['GET'])
        def ShutdownQE():
            if qe_status() == 0:
                qe_status("set", 2)
                return """<!DOCTYPE html><html><head><style>body { background-color: #161616; color: white; font-family: sans-serif; padding: 2em; }</style></head><body><h2>Now shutting down QuantumENDEC...</h2></body></html>"""
            
            if qe_status() == 1:
                qe_status("set", 2)
                return """<!DOCTYPE html><html><head><style>body { background-color: #161616; color: white; font-family: sans-serif; padding: 2em; }</style></head><body><h2>QuantumENDEC was already restarting, now shutting down...</h2></body></html>"""
            
            if qe_status() == 2:
                return """<!DOCTYPE html><html><head><style>body { background-color: #161616; color: white; font-family: sans-serif; padding: 2em; }</style></head><body><h2>QuantumENDEC is already in the process of shutting down...</h2></body></html>"""
            
            #return """Now shutting down QuantumENDEC..."""
        
        @self.QEWEB_flaskapp.route('/alertText')
        def GetAlertText():
            try:
                alertText = load_json(f"{assets_folder}/cgen.json")
                return jsonify(alertText)
            except:
                nothingThing = { "headline":"EMERGENCY ALERT DETAILS", "text":"", "background_color":"000000", "text_color":"ffffff", "alert_status":False }
                return jsonify(nothingThing)

        @self.QEWEB_flaskapp.before_request
        def require_login():
            public_paths = ['/login', '/login.html', '/scroll.html', '/alertText', '/fullscreen.html', '/tmp/alert_image.png', '/fullscreen_image.html', '/Jstyle.html', '/scroll_fancy.html']
            if request.path not in public_paths:
                if not self.is_authenticated(): return redirect(url_for('login'))

        @self.QEWEB_flaskapp.route('/change_password', methods=['POST'])
        def change_password():
            if not self.is_authenticated(): return 'Unauthorized.', 401
            data = request.get_json()
            current_password_hash = hashlib.sha256(data['currentPassword'].encode()).hexdigest()
            new_password_hash = hashlib.sha256(data['newPassword'].encode()).hexdigest()
            if current_password_hash == self.load_password():
                self.save_password(new_password_hash)
                self.SESSIONS.clear() # Clear all sessions
                return 'Password changed successfully.', 200
            else: return 'Incorrect current password.', 403
        
        @self.QEWEB_flaskapp.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                data = request.json
                password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
                if password_hash == self.load_password():
                    session_id = self.create_session()
                    response = jsonify(message='Login successful.')
                    response.set_cookie(self.SESSION_COOKIE_NAME, session_id, httponly=True)
                    return response
                else: return jsonify(message='Incorrect password.'), 403
            return send_from_directory(assets_folder, 'login.html')
            #return make_response(open('login.html').read()) # Render login page if GET request

        @self.QEWEB_flaskapp.route('/logout', methods=['POST'])
        def logout():
            session.clear()  # Clear all session data
            response = make_response(redirect('/login.html')) # Create a response object
            response.set_cookie(self.SESSION_COOKIE_NAME, '', expires=0) # Remove the session cookie
            return response
        
        @self.QEWEB_flaskapp.route('/')
        def home(): return send_from_directory(assets_folder, 'index.html')

        @self.QEWEB_flaskapp.route('/<path:path>')
        def static_files(path): return send_from_directory(assets_folder, path)

        @self.QEWEB_flaskapp.after_request
        def add_header(response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response
        
        @self.QEWEB_flaskapp.route('/config_data')
        def config_data():
            try: CONFIG_DATA = load_json(f"{assets_folder}/config.json")
            except: CONFIG_DATA = default_config
            return jsonify(CONFIG_DATA)

        @self.QEWEB_flaskapp.route('/audio_outputs')
        def audio_outputs():
            devices = get_audio_outputs()
            return jsonify(devices)

        @self.QEWEB_flaskapp.route('/tts_voices')
        def tts_voices():
            voices = list_tts_voices()
            return jsonify(voices)
        
        @self.QEWEB_flaskapp.route('/maki_voices')
        def maki_voices():
            try:
                if (get_platform() == "win") and os.path.exists("./Maki.exe"):
                    app_command = "./Maki.exe"
                    list_output = subprocess.run([app_command, "--list-voices"], capture_output=True, text=True)
                    list_output = list_output.stdout.split("|")
                    voices = []
                    for voice in list_output:
                        if voice == "": pass
                        elif voice == "\n": pass
                        else: voices.append(voice)
                    return jsonify(voices)
                else: return jsonify([])
            except: return jsonify([])

        @self.QEWEB_flaskapp.route('/upload_config', methods=['POST'])
        def upload_config():
            if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
            file = request.files['file']    
            if file.filename == '': return jsonify({'error': 'No selected file'}), 400
            if not file.filename.endswith('.json'): return jsonify({'error': 'Only JSON files are accepted'}), 400
            file.save(f"{assets_folder}/config.json")
            return jsonify({'success': f'File uploaded and saved as {assets_folder}/config.json'}), 200

        @self.QEWEB_flaskapp.route('/upload_leadin', methods=['POST'])
        def upload_leadin():
            SAVE_PATH = f'{assets_folder}/pre.wav'
            if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
            file = request.files['file']    
            if file.filename == '': return jsonify({'error': 'No selected file'}), 400
            if not file.filename.endswith('.wav'): return jsonify({'error': 'Only wav files are accepted'}), 400
            file.save(SAVE_PATH)
            return jsonify({'success': 'File uploaded and saved'}), 200

        @self.QEWEB_flaskapp.route('/upload_leadout', methods=['POST'])
        def upload_leadout():
            SAVE_PATH = f'{assets_folder}/post.wav'
            if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
            file = request.files['file']    
            if file.filename == '': return jsonify({'error': 'No selected file'}), 400
            if not file.filename.endswith('.wav'): return jsonify({'error': 'Only wav files are accepted'}), 400
            file.save(SAVE_PATH)
            return jsonify({'success': 'File uploaded and saved'}), 200

        @self.QEWEB_flaskapp.route('/remove_Leadin', methods=['POST'])
        def removeLeadin():
            try:
                delete_file(f"{assets_folder}/pre.wav")
                return jsonify({'success': 'Lead in audio removed'})
            except: return jsonify({'error': 'Failed to remove Lead in audio'})
            
        @self.QEWEB_flaskapp.route('/remove_Leadout', methods=['POST'])
        def removeLeadout():
            try:
                delete_file(f"{assets_folder}/post.wav")
                return jsonify({'success': 'Lead out audio removed'})
            except: return jsonify({'error': 'Failed to remove Lead out audio'})

        @self.QEWEB_flaskapp.route('/submit_alert', methods=['POST'])
        def submit_alert():
            form_data = request.form.to_dict()
            # types (in values): text, bool, list
            valid_options = {
                "ORG": "text",
                "EVE": "text",
                "FIPS": "text",
                "primarylanguage_language": "text",
                "primarylanguage_broadcasttext": "text",
                "secondlanguage_send": "bool",
                "secondlanguage_language": "text",
                "secondlanguage_broadcasttext": "text"
            }
            send_alert_dict = {}
            for key, value in valid_options.items():
                if key in form_data:
                    if value == "bool":
                        if form_data[key] == "on": send_alert_dict[key] = True
                        else: send_alert_dict[key] = False
                    else: send_alert_dict[key] = str(form_data[key])
                else:
                    if value == "bool": send_alert_dict[key] = False
                    elif value == "list": send_alert_dict[key] = []
                    else: send_alert_dict[key] = ""
            nowTime = datetime.now(timezone.utc)
            sent = nowTime.strftime('%Y-%m-%dT%H:%M:%S-00:00')
            expire = nowTime + timedelta(hours=1)
            expire = expire.strftime('%Y-%m-%dT%H:%M:%S-00:00')
            sentforres = nowTime.strftime('%Y%m%dT%H%M%S')
            res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
            identifier = f"{res}{sentforres}"
            same_event = send_alert_dict['EVE']
            same_originator =  send_alert_dict['ORG']
            same_fips = send_alert_dict['FIPS']
            if same_event == "": same_event = "DMO"
            if same_originator == "": same_originator = "EAS"
            if same_fips == "": same_fips = "000000"
            try: category = same2cap_org[same_originator]
            except: category = "Other"
            same_event = same_event.upper()
            same_event = same_event[:3]
            zczc = f"ZCZC-{same_originator}-{same_event}-{same_fips}+0100-1001200-INTERNAL-".replace("\n", "")
            lolz = EAS2Text(zczc)
            areaDesc = ",".join(lolz.FIPSText)
            if send_alert_dict['secondlanguage_send'] is True:
                second_info_block = f"""
                <info>
                    <language>{send_alert_dict['secondlanguage_language']}</language>
                    <category>{category}</category>
                    <event>{lolz.evntText}</event>
                    <urgency>Unknown</urgency>
                    <severity>Unknown</severity>
                    <certainty>Unknown</certainty>
                    <effective>{sent}</effective>
                    <expires>{expire}</expires>
                    <eventCode><valueName>SAME</valueName><value>{same_event}</value></eventCode>
                    <senderName>QuantumENDEC Internal</senderName>
                    <headline>{lolz.evntText}</headline>
                    <description>{send_alert_dict['secondlanguage_broadcasttext']}</description>
                    <parameter><valueName>layer:SOREM:1.0:Broadcast_Text</valueName><value>{send_alert_dict['secondlanguage_broadcasttext']}</value></parameter>
                    <parameter><valueName>EAS-ORG</valueName><value>{same_originator}</value></parameter>
                    <area><areaDesc>{areaDesc}</areaDesc><geocode><valueName>SAME</valueName><value>{same_fips}</value></geocode></area>
                </info>
                """
            else: second_info_block = ""
            finalXML = f"""
            <alert>
                <identifier>{res}</identifier>
                <sender>QuantumENDEC Internal</sender>
                <sent>{sent}</sent>
                <status>Actual</status>
                <msgType>Alert</msgType>
                <source>QuantumENDEC Self Alert Orginator</source>
                <scope>Public</scope>
                <info>
                    <language>{send_alert_dict['primarylanguage_language']}</language>
                    <category>{category}</category>
                    <event>{lolz.evntText}</event>
                    <urgency>Unknown</urgency>
                    <severity>Unknown</severity>
                    <certainty>Unknown</certainty>
                    <effective>{sent}</effective>
                    <expires>{expire}</expires>
                    <eventCode><valueName>SAME</valueName><value>{same_event}</value></eventCode>
                    <senderName>QuantumENDEC Internal</senderName>
                    <headline>{lolz.evntText}</headline>
                    <description>{send_alert_dict['primarylanguage_broadcasttext']}</description>
                    <parameter><valueName>layer:SOREM:1.0:Broadcast_Text</valueName><value>{send_alert_dict['primarylanguage_broadcasttext']}</value></parameter>
                    <parameter><valueName>EAS-ORG</valueName><value>{same_originator}</value></parameter>
                    <area><areaDesc>{areaDesc}</areaDesc><geocode><valueName>SAME</valueName><value>{same_fips}</value></geocode></area>
                </info>
                {second_info_block}
            </alert>
            """
            filenameXML = f"{queue_folder}/{sent.replace(':', '_')}I{res}.xml"
            print(f"[Webserver]: Creating alert: {filenameXML}")
            write_file(finalXML, filenameXML)
            return """<!DOCTYPE html><html><head><title>QuantumENDEC Web Interface</title><link rel="stylesheet" href="./style.css"></head><body><h1>Alert sent.</h1><a class="button" href="/">OK</a></body></html>"""

        @self.QEWEB_flaskapp.route('/submit_config', methods=['POST'])
        def submit():
            form_data = request.form.to_dict()
            new_config = { "quantumendec_version":QuantumENDEC_Version }
            for key, value in valid_configs.items():
                if key in form_data:
                    if value == "bool":
                        if form_data[key] == "on": new_config[key] = True
                        else: new_config[key] = False
                    elif value == "list":
                        if form_data[key] == "": new_config[key] = []
                        else: new_config[key] = form_data[key].split(",")
                    else: new_config[key] = str(form_data[key])
                else:
                    if value == "bool": new_config[key] = False
                    elif value == "list": new_config[key] = []
                    else: new_config[key] = ""
            # Protection just incase someone screws up the web server settings.
            PORT = new_config["webserver_port"]
            try:
                if int(PORT) > 65535: PORT = "80"
                if int(PORT) < 0: PORT = "80"
                if PORT == "": PORT = "80"
            except: PORT = "80"
            new_config["webserver_port"] = PORT
            HOST = new_config["webserver_host"]
            if HOST == "": HOST = "0.0.0.0"
            new_config["webserver_host"] = HOST
            write_json(f"{assets_folder}/config.json", new_config)
            return """<!DOCTYPE html><html><head><title>QuantumENDEC Web Interface</title><link rel="stylesheet" href="./style.css"></head><body><h1>Your settings has been saved.</h1><a class="button" href="/">OK</a></body></html>"""
        
    def Start(self):
        print("[Webserver]: Starting webserver... ", f"HOST: {self.HOST} PORT: {self.PORT}")
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        self.QEWEB_flaskapp.run(host=self.HOST, port=self.PORT, debug=False)

class Logger:
    def __init__(self, config_data={}, headline="", description="", alert_color="ffffff", mode="TX", zczc=None):
        self.headline = headline
        self.description = description
        self.mode = mode
        self.alert_color = alert_color
        self.config_data = config_data
        self.zczc = zczc
    
    def txt_logger(self):
        dateNow = datetime.now().strftime("%B %d, %Y %H:%M:%S")
        if ((self.zczc == "") or (self.zczc is None)): log = f"{self.headline}\n{self.description}"
        else: log = f"{self.headline}\n{self.description}\n{self.zczc}"
        log = f"\n--- {dateNow} ---\n{log}\n"
        append_file(log, f"{assets_folder}/alertlog.txt")

    def email_logger(self):
        sender_email = self.config_data["email_user"]
        sender_password = self.config_data["email_userPassword"]
        smtp_server = self.config_data["email_SMTPserver"]
        smtp_port = int(self.config_data["email_SMTPport"])
        recipient_emails = self.config_data["email_recipients"]
        callsign = str(self.config_data["SAME_callsign"])
        headline = str(self.headline)
        description = str(self.description)
        zczc = str(self.zczc)

        date = datetime.now()
        date = date.astimezone()
        date = date.strftime("%H:%M%z %d/%m/%Y")

        subject = f"QuantumENDEC Email Log: {headline}"
        body = f"""QuantumENDEC Email Log\n{date}\n\nStation: {callsign}\n\n{headline}\n\n{description}\n\n{zczc}"""

        msg = MIMEMultipart()
        msg['From'] = sender_email
        #msg['To'] = ", ".join(recipient_emails)
        msg['To'] = recipient_emails
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                try: server.starttls()
                except: pass
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_emails, msg.as_string())
                print("[LOGGER]: Email sent successfully.")
        except Exception as e: print(f"[LOGGER]: Failed to send email: {e}")

    def discord_logger(self):
        webhook_author_name = self.config_data['discordwebhook_author_name']
        webhook_author_URL = self.config_data['discordwebhook_author_URL']
        webhook_author_iconURL = self.config_data['discordwebhook_author_iconURL']
        webhook_URL = self.config_data['discordwebhook_URL']
        webhook_sendAudio = self.config_data['discordwebhook_sendAudio']
        webhook_sendImage = self.config_data['discordwebhook_sendImage']
        
        if self.description is None: alert_description = ""
        else:
            alert_description = self.description.replace("/n", " ")
            if len(alert_description) > 2000: alert_description = f"{alert_description[:2000]}..."
        
        webhook = DiscordWebhook(url=webhook_URL, rate_limit_retry=True)
        
        # Send audio and image (if enabled)
        if self.mode == "TX":
            if webhook_sendAudio is True:
                try:
                    subprocess.run(["ffmpeg", "-y", "-i", f"{tmp_folder}/audio.wav", "-map", "0:a:0", "-b:a", "64k", f"{tmp_folder}/discord_audio.mp3"], capture_output=True, text=True)
                    with open(f"{tmp_folder}/discord_audio.mp3", "rb") as f: webhook.add_file(file=f.read(), filename="audio.mp3")
                except: pass
            if (webhook_sendImage is True) and (self.config_data["produce_alertimage"] is True):
                try:
                    with open(f"{tmp_folder}/alert_image.png", "rb") as f: webhook.add_file(file=f.read(), filename="image.png")
                except: pass

        if (self.alert_color is None) or (self.alert_color == ""): webhook_color = "ffffff"
        else: webhook_color = self.alert_color
        
        embed = DiscordEmbed(title=self.headline, description=alert_description, color=webhook_color,)
        
        if (self.zczc == "") or (self.zczc is None): pass
        else:
            alert_zczc = self.zczc.replace("/n", " ")
            if len(alert_zczc) > 1000: alert_zczc = f"{alert_zczc[:1000]}..."
            alert_zczc = f"```{alert_zczc}```"
            embed.add_embed_field(name="", value=alert_zczc, inline=False)
        
        embed.set_author(name=webhook_author_name, url=webhook_author_URL, icon_url=webhook_author_iconURL)
        embed.set_footer(text="Powered by QuantumENDEC")
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()

    def SendLog(self):
        try: self.txt_logger()
        except Exception as e: print("[LOGGER]: TXT log failure. ", e)

        try:
            if (self.config_data["discordwebhook_enable"] is True) and (DiscordWebhook_available is True): self.discord_logger()
        except Exception as e: print("[LOGGER]: Discord failure. ", e)

        try:
            if self.config_data["email_enable"] is True: self.email_logger()
        except Exception as e: print("[LOGGER]: Email failure. ", e)

class Capture:
    def SaveCAP(self, OutputFolder, InputXML, Source=None):
        CapturedSent = re.search(r'<sent>\s*(.*?)\s*</sent>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
        CapturedIdent = re.search(r'<identifier>\s*(.*?)\s*</identifier>', InputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
        filename = f"{CapturedSent}I{CapturedIdent}.xml"
        write_file(InputXML, f"{OutputFolder}/{filename}")
        print(f"[Capture]: Captured an XML, and saved it to: {OutputFolder}/{filename} | From: {Source}")

    def realTCPcapture(self, host, port, buffer=1024, delimiter="</alert>", StatName=None):
        print(f"[TCP Capture]: Connecting to: {host} at {port}")
        while qe_status() == 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((host, int(port)))
                    s.settimeout(100)
                    if StatName is not None: set_status(StatName, f"Connected to {host}")
                    print(f"[TCP Capture]: Connected to {host}")
                    data_received = ""
                    try:
                        while qe_status() == 0:
                            chunk = str(s.recv(buffer), encoding='utf-8', errors='ignore')
                            data_received += chunk
                            if delimiter in chunk:
                                try: self.SaveCAP(queue_folder, data_received, host)
                                except: print(f"[TCP Capture]: {StatName}, failed to save XML!")
                                data_received = ""
                    except socket.timeout:
                        print(f"[TCP Capture]: Connection timed out for {host}")
                        if StatName is not None: set_status(StatName, f"Timed out: {host}")
                except Exception as e:
                    print(f"[TCP Capture]: Something broke when connecting to {host}: {e}")
                    if StatName is not None: set_status(StatName, f"Connection error to: {host}")
        exit()

    def TCP(self, host, port, buffer=1024, delimiter="</alert>", StatName=None):
        # i hate this, but it results in quicker shutdowns/restarts
        decodeThread = threading.Thread(target=self.realTCPcapture, args=(host, port, buffer, delimiter, StatName))
        decodeThread.daemon = True
        decodeThread.start()
        while qe_status() == 0: time.sleep(1) # keep-alive
        exit()

    def HTTP(self, CAP_URL, instance=None):
        if CAP_URL is None or CAP_URL == "": set_status(f"HTTPCAPcapture{instance}", f"HTTP CAP capture {instance} disabled.")
        else:
            print(f"[HTTP Capture]: HTTP CAP Capture active! {CAP_URL}")
            while qe_status() == 0:
                try:
                    set_status(f"HTTPCAPcapture{instance}", f"HTTP CAP Capture {instance} is active!")
                    ReqCAP = Request(url = f'{CAP_URL}')
                    CAP = urlopen(ReqCAP).read()
                    CAP = CAP.decode('utf-8')
                    CAP = re.findall(r'<alert\s*(.*?)\s*</alert>', CAP, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    for alert in CAP:
                        alert = f"<alert {alert}</alert>"
                        try: self.SaveCAP(queue_folder, alert, CAP_URL)
                        except: print("[Capture]: Failed to save XML!")
                    time.sleep(30)
                except Exception as e:
                    print("[HTTP Capture] Something went wrong.", e)
                    set_status(f"HTTPCAPcapture{instance}", f"HTTP CAP Capture {instance} error.")
                    time.sleep(30)

    def NWS(self, ATOM_LINK):
        # Goddamnit americans, you have to have every single alert source in their own goddamn way!
        # Why can't you use a centerlized TCP server?!!?!
        print("[NWS CAP Capture]: Activating NWS CAP Capture with: ", ATOM_LINK)
        while qe_status() == 0:
            set_status("NWSCAPcapture", "NWS CAP Capture is active.")
            try:
                req1 = Request(url = ATOM_LINK)
                xml = urlopen(req1).read()
                xml = xml.decode('utf-8')
                entries = re.findall(r'<entry>\s*(.*?)\s*</entry>', xml, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                current_time = datetime.now(timezone.utc)
                for entry in entries:
                    try:
                        CAP_LINK = re.search(r'<link\s*rel="alternate"\s*href="\s*(.*?)\s*"/>', entry, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        expires = re.search(r'<cap:expires>\s*(.*?)\s*</cap:expires>', entry, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        expires = datetime.fromisoformat(expires).astimezone(timezone.utc).isoformat()
                        expires = datetime.fromisoformat(expires)

                        if current_time > expires: pass #print("expired")
                        else:        
                            last_slash_index = CAP_LINK.rfind('/')
                            if last_slash_index != -1: filename = CAP_LINK[last_slash_index + 1:]
                            else: filename = CAP_LINK 
                            filename = filename.replace("-", "_").replace("+", "p").replace(":", "_").replace("\n", "")
                            filename = filename + ".xml"
                            if filename in os.listdir(f"{history_folder}"): pass #print("already downloaded")
                            elif filename in os.listdir(f"{queue_folder}"): pass #print("already downloaded")
                            else:
                                # print(filename, expires)
                                NWSCAP_REQUEST = Request(url = CAP_LINK)
                                NWSCAP_XML = urlopen(NWSCAP_REQUEST).read()
                                NWSCAP_XML = NWSCAP_XML.decode('utf-8')
                                write_file(NWSCAP_XML, f"{queue_folder}/{filename}")
                    except: pass
            except Exception as e:
                print("[NWS CAP Capture]: An error occured.", e)
                set_status("NWSCAPcapture", "An error occured.")
            time.sleep(120) # To put less strain on the network

class Monitor_Stream:
    def __init__(self, monitorName, streamURL, ConfigData={}):
        self.monitorName = monitorName
        self.streamURL = streamURL
        self.record = False
        self.ConfigData = ConfigData

    def is_stream_online(self):
        try:
            response = requests.get(self.streamURL, stream=True, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"[{self.monitorName}] Error checking stream URL: {e}")
            return False
    
    def RecordIP(self, ZCZC):
        output_file = f"{tmp_folder}/{self.monitorName}-audio.wav"
        try: os.remove(output_file)
        except: pass
        RecordIP = (ffmpeg .input(self.streamURL) .output(output_file, format='wav', ar='8000') .run_async(pipe_stdout=True, pipe_stderr=True))
        seconds = 0
        while qe_status() == 0:
            seconds = seconds + 1
            if self.record is False or seconds == 120 or seconds > 120:
                RecordIP.terminate()
                RecordIP.wait()
                print(f"[{self.monitorName}] Stopped Recording Thread")
                Remove_EOMandATTN(output_file)
                CreateXML_from_MonitorSAME(ZCZC, output_file, self.monitorName)
                set_status(self.monitorName, f"Alert sent.")
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
            platform = get_platform()
            last = None
            self.ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
            if platform == "win": self.source_process = subprocess.Popen(['multimon-ng-WIN32/multimon-ng.exe', '-a', 'EAS', '-q', '-t', 'raw', '-'], stdin=self.ffmpeg_process.stdout, stdout=subprocess.PIPE)
            else: self.source_process = subprocess.Popen(['multimon-ng', '-a', 'EAS', '-q', '-t', 'raw', '-'], stdin=self.ffmpeg_process.stdout, stdout=subprocess.PIPE)
            set_status(self.monitorName, f"Ready For Alerts, listening to {self.streamURL}")
            print(f"[{self.monitorName}]  Ready For Alerts, listening to {self.streamURL}\n")

            while qe_status() == 0:
                line = self.source_process.stdout.readline().decode("utf-8")
                if qe_status() != 0: break
                decode = line.replace("b'EAS: ", "").replace("\n'", "").replace("'bEnabled Demodulators: EAS", "").replace('EAS:  ', '').replace('EAS: ', '').replace('Enabled demodulators: EAS', '')
                if "ZCZC-" in decode or "NNNN" in decode: print(f"[{self.monitorName}]  Decoder: {decode}")

                if 'ZCZC-' in str(line):
                    if ZCZC_test(decode) == True:
                        SAME = decode.replace("\n", "")
                        set_status(self.monitorName, f"Receiving alert...")
                        print(f"[{self.monitorName}] ZCZC Check OK")
                        dateNow = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
                        Logger(self.ConfigData, "Emergency Alert Received", f"Receipt: Received on {dateNow} from {self.monitorName}", "ffffff", "RX", SAME).SendLog()
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
                        set_status(self.monitorName, f"Ready For Alerts, listening to {self.streamURL}")
                last = line
        except Exception as e:
            try:
                self.ffmpeg_process.terminate()
                self.source_process.terminate()
            except: pass
            set_status(self.monitorName, f"Failure")
            print(f"[{self.monitorName}] Monitor failure. {e}")

    def Start(self):
        while qe_status() == 0:
            if self.is_stream_online() is False:
                print(f"[{self.monitorName}] Stream URL {self.streamURL} is offline or unreachable.")
                set_status(self.monitorName, f"Stream URL {self.streamURL} is offline or unreachable.")
                time.sleep(30)
            else:
                try:
                    decodeThread = threading.Thread(target=self.decodeStream)
                    decodeThread.daemon = True
                    decodeThread.start()
                    while qe_status() == 0:
                        time.sleep(30)
                        if self.is_stream_online() is False:
                            print(f"[{self.monitorName}] Stream URL {self.streamURL} is offline or unreachable.")
                            set_status(self.monitorName, f"Stream URL {self.streamURL} is offline or unreachable.")
                            time.sleep(30)
                            break
                        else: pass
                    if qe_status() != 0:
                        self.ffmpeg_process.terminate()
                        self.source_process.terminate()
                except Exception as e:
                    print(f"[{self.monitorName}] Monitor failure.")
                    set_status(self.monitorName, f"Failure. {e}")
        exit()

class Monitor_Local:
    def __init__(self, monitorName, ConfigData={}):
        self.monitorName = monitorName
        self.record = False
        self.ConfigData = ConfigData

    def recordAUDIO(self, SAME):
        OutputFile = f"{tmp_folder}/{self.monitorName}-audio.wav"
        try: os.remove(OutputFile)
        except: pass
        while qe_status() == 0:
            sd.default.reset()
            samplerate = 8000
            q = queue.Queue()

            def callback(indata, frames, time, status):
                if status: print(status, file=sys.stderr)
                q.put(indata.copy())

            with sf.SoundFile(OutputFile, mode='x', samplerate=samplerate,channels=2) as file:
                with sd.InputStream(samplerate=samplerate,channels=2,callback=callback):
                    print(f"[{self.monitorName}] Recording!")
                    last_check_time = time.time()
                    while qe_status() == 0:
                        file.write(q.get())
                        current_time = time.time()
                        if self.record is False or current_time - last_check_time > 120:
                            file.close()
                            print(f"[{self.monitorName}] Stopped Recording Thread")
                            Remove_EOMandATTN(OutputFile)
                            CreateXML_from_MonitorSAME(SAME, OutputFile, self.monitorName)
                            set_status(self.monitorName, f"Alert sent.")
                            print(f"[{self.monitorName}]  Alert Sent!")
                            exit()
        exit()

    def DecodeDev(self):
        while qe_status() == 0:
            try:
                platform = get_platform()
                last = None
                if platform == "win": self.source_process = subprocess.Popen(["multimon-ng-WIN32/multimon-ng.exe", "-a", "EAS", "-q"], stdout=subprocess.PIPE)
                else: self.source_process = subprocess.Popen(["multimon-ng", "-a", "EAS", "-q"], stdout=subprocess.PIPE)
                set_status(self.monitorName, f"Ready For Alerts.")
                print(f"[{self.monitorName}]  Ready For Alerts...\n")

                while qe_status() == 0:
                    line = self.source_process.stdout.readline().decode("utf-8")
                    if qe_status() != 0: break
                    decode = line.replace("b'EAS: ", "").replace("\n'", "").replace("'bEnabled Demodulators: EAS", "").replace('EAS:  ', '').replace('EAS: ', '').replace('Enabled demodulators: EAS', '')
                    if "ZCZC-" in decode or "NNNN" in decode: print(f"[{self.monitorName}]  Decoder: {decode}")

                    if 'ZCZC-' in str(line):
                        if ZCZC_test(decode) == True:
                            SAME = decode.replace("\n", "")
                            set_status(self.monitorName, f"Receiving alert...")
                            print(f"[{self.monitorName}] ZCZC Check OK")
                            dateNow = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
                            Logger(self.ConfigData, "Emergency Alert Received", f"Receipt: Received on {dateNow} from {self.monitorName}", "ffffff", "RX", SAME).SendLog()
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
                            set_status(self.monitorName, f"Ready For Alerts.")
                    last = line
            except Exception as e:
                set_status(self.monitorName, f"Failure")
                print(f"[{self.monitorName}] Monitor failure.", e)
                time.sleep(5)
        exit()
    
    def Start(self):
        try:
            decodeThread = threading.Thread(target=self.DecodeDev)
            decodeThread.daemon = True
            decodeThread.start()
            while qe_status() == 0: time.sleep(1) # keep-alive
            self.source_process.terminate()
            exit()
        except:
            print(f"[{self.monitorName}] Monitor failure.")
            set_status(self.monitorName, f"Failure.")

class Generate_AlertMap:
    def __init__(self, image_output, polygon_color="#ff0000", headline="", polygon_coords=[]):
        self.ImageOutput = image_output
        self.polygon_color = polygon_color
        self.polygon_coords = polygon_coords
        self.headline = headline

    def overlay_polygon(self, ax, lats, lons, label='', color='red'):
        ax.plot(lons, lats, color=color, linewidth=2, linestyle='-', label=label, transform=ccrs.PlateCarree())

    def fill_polygon(self, ax, lats, lons, color='red', alpha=0.5):
        polygon = Polygon(list(zip(lons, lats)), facecolor=color, alpha=alpha, transform=ccrs.PlateCarree())
        ax.add_patch(polygon)

    def calculate_bounding_box(self, coordinates):
        min_lat = min(lat for lat, _ in coordinates)
        max_lat = max(lat for lat, _ in coordinates)
        min_lon = min(lon for _, lon in coordinates)
        max_lon = max(lon for _, lon in coordinates)
        return min_lat, max_lat, min_lon, max_lon

    def generate_map(self):
        matplotlib.use('Agg')
        polygon_color = self.polygon_color
        if "#" not in polygon_color: polygon_color = "#" + polygon_color
        if len(polygon_color) > 7: polygon_color = "#FF0000"
        for char in polygon_color:
            if 'G' <= char <= 'Z' or 'g' <= char <= 'z': polygon_color = "#FF0000"
        
        # Generate map
        coordinates_string = ""
        for i in self.polygon_coords: coordinates_string += f" {i}"
        polygon_coordinates = [list(map(float, item.split(','))) for item in coordinates_string.split()]
        min_lat, max_lat, min_lon, max_lon = self.calculate_bounding_box(polygon_coordinates)

        lat_center = (min_lat + max_lat) / 2
        lon_center = (min_lon + max_lon) / 2
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon

        if lat_range > lon_range: lon_range = lat_range
        else: lat_range = lon_range

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

        # Set map extent
        ax.set_extent([
            lon_center - 1.1 * lon_range, lon_center + 1.1 * lon_range,
            lat_center - 1.1 * lat_range, lat_center + 1.1 * lat_range
        ])

        # Add map features
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.STATES, linestyle='--')
        ax.add_feature(cfeature.LAND, facecolor='#00AA44')
        ax.add_feature(cfeature.OCEAN, facecolor='#002255')
        ax.add_feature(cfeature.LAKES, facecolor='#002255')

        if os.path.exists("./map_addons/counties/ne_10m_admin_2_counties.shp"):
            print("counties shapefile detected")
            countines = cfeature.ShapelyFeature(
                shpreader.Reader("./map_addons/counties/ne_10m_admin_2_counties.shp").geometries(),
                ccrs.PlateCarree(),
                facecolor='none', edgecolor='black' )
            ax.add_feature(countines)

        if os.path.exists("./map_addons/roads/ne_10m_roads.shp"):
            print("roads shapefile detected")
            roads = cfeature.ShapelyFeature(
                shpreader.Reader("./map_addons/roads/ne_10m_roads.shp").geometries(),
                ccrs.PlateCarree(),
                facecolor='none', edgecolor='white' )
            ax.add_feature(roads)

        # Draw polygons
        for i in self.polygon_coords:
            i = [list(map(float, item.split(','))) for item in i.split()]
            lats, lons = zip(*i)
            self.fill_polygon(ax, lats, lons, color=polygon_color, alpha=0.6)
            self.overlay_polygon(ax, lats, lons, label=self.headline, color=polygon_color)  # For outlined polygon

        if os.path.exists("./map_addons/populations/ne_10m_populated_places.shp"):
            print("population shapefiles detected")
            label_field = "NAME"
            color = "black"
            reader = shpreader.Reader("./map_addons/populations/ne_10m_populated_places.shp")
            
            # Function to check if a point is within the bounding box
            def is_within_bbox(x, y, bbox):
                min_lon, max_lon, min_lat, max_lat = bbox
                return min_lon <= x <= max_lon and min_lat <= y <= max_lat

            for record in reader.records():
                geometry = record.geometry
                if geometry.geom_type == "Point":
                    # Check if the point is within the bounding box
                    if is_within_bbox(geometry.x, geometry.y, (min_lon, max_lon, min_lat, max_lat)):
                        # Plot the point
                        ax.plot(geometry.x, geometry.y, 'o', color=color, transform=ccrs.PlateCarree())
                        
                        # Add label (if available)
                        label = record.attributes.get(label_field, "Unknown")
                        ax.text(geometry.x, (geometry.y + 0.05), label, fontsize=8, color=color, transform=ccrs.PlateCarree())

        ax.set_aspect('auto')
        legend_patch = Line2D([0], [0], marker='o', color='w', markerfacecolor=polygon_color, markersize=10, label=self.headline)
        plt.legend(handles=[legend_patch], loc='upper right')
        fig.savefig(self.ImageOutput, bbox_inches='tight', pad_inches=0.0, dpi=70)

class Generate_Text:
    def __init__(self, CONFIG_DATA={}, INFODICT={}, MESSAGE_TYPE=None, SENT_ISO=None):
        """ generate broadcast text and the ZCZC code from CAP """
        self.CONFIG_DATA = CONFIG_DATA
        self.INFODICT = INFODICT
        self.MESSAGE_TYPE = str(MESSAGE_TYPE)
        self.SENT_ISO = SENT_ISO
        Language = INFODICT.get("language")
        if "en-ca" in Language or "en-us" in Language or "en" in Language: self.Language = "EN"
        elif "fr-ca" in Language or "fr" in Language: self.Language = "FR"
        else: self.Language = "NOT_SUPPORTED"

    def create_text(self):
        parameters_dict = self.INFODICT.get("parameter")
        try: broadcast_text = get_cap_value(parameters_dict, "valueName", "layer:SOREM:1.0:Broadcast_Text").get("value")
        except:
            try:
                areas = self.INFODICT.get("area")
                if isinstance(areas, dict): areas = [areas]
                AreaDesc = []
                for area in areas:
                    x = area.get("areaDesc")
                    if x is not None: AreaDesc.append(x)
                AreaDesc = ', '.join(AreaDesc) + '.'
            except: AreaDesc = None

            try: Headline = f"{self.INFODICT.get("headline")}."
            except: Headline = None
            try: Description = self.INFODICT.get("description")
            except: Description = None
            try: Instruction = self.INFODICT.get("instruction")
            except: Instruction = None

            if Description is None: Description = ""
            if Instruction is None: Instruction = ""
            if Headline is None: Headline = ""
            if AreaDesc is None: AreaDesc = ""

            broadcast_text = f"{Headline} {AreaDesc}. {Description} {Instruction}"
            broadcast_text = broadcast_text.replace('###','').replace('  ',' ').replace('..','.').replace("\n", " ")

        return broadcast_text

    def create_zczc(self):
        parameters_dict = self.INFODICT.get("parameter")

        try: ORG = get_cap_value(parameters_dict, "valueName", "EAS-ORG").get("value")
        except:
            try: ORG = cap2same_org[str(self.INFODICT.get("category"))]
            except: ORG = "CIV"

        try:
            EVE = get_cap_value(self.INFODICT.get("eventCode"), "valueName", "SAME").get("value")
            if EVE is None or EVE == "": EVE = "CEM"
        except:
            try: EVE = cap2same_event[str(get_cap_value(self.INFODICT.get("eventCode"), "valueName", "profile:CAP-CP:Event:0.4").get("value"))]
            except: EVE = "CEM"

        try: LOCATION_CODES = get_cap_value(parameters_dict, "valueName", "layer:EC-MSC-SMC:1.1:Newly_Active_Areas").get("value").replace(",","-")
        except:
            try:
                GeocodeList = []
                areas = self.INFODICT.get("area")
                if isinstance(areas, dict): areas = [areas]
                for area in areas:
                    geocodes = area.get("geocode")
                    x = get_cap_value(geocodes, "valueName", "profile:CAP-CP:Location:0.3")
                    if x is not None: GeocodeList.append(str(x.get("value")))
                geocode2clc = grab_geotoclc()
                locationcodes_list = []
                for geocode in GeocodeList:
                    new_code = geocode2clc[geocode]
                    if new_code not in locationcodes_list: locationcodes_list.append(new_code)
                LOCATION_CODES = '-'.join(locationcodes_list)
                if (len(locationcodes_list) == 0) or LOCATION_CODES == "": raise Exception
            except:
                try:
                    locationcodes_list = []
                    areas = self.INFODICT.get("area")
                    if isinstance(areas, dict): areas = [areas]
                    for area in areas:
                        geocodes = area.get("geocode")
                        x = get_cap_value(geocodes, "valueName", "SAME")
                        if x is not None: locationcodes_list.append(str(x.get("value")))
                    LOCATION_CODES = '-'.join(locationcodes_list)
                    if (len(locationcodes_list) == 0) or LOCATION_CODES == "": raise Exception
                except: LOCATION_CODES = "000000"

        try:
            NowTime = datetime.now(timezone.utc)
            NowTime = NowTime.replace(microsecond=0).isoformat()
            NowTime = NowTime[:-6]
            NowTime = datetime.fromisoformat(NowTime)
            ExpireTime = self.INFODICT.get("expires")
            ExpireTime = datetime.fromisoformat(ExpireTime).astimezone(timezone.utc)
            ExpireTime = ExpireTime.isoformat()
            ExpireTime = ExpireTime[:-6]
            ExpireTime = datetime.fromisoformat(ExpireTime)
            Purge = ExpireTime - NowTime
            hours, remainder = divmod(Purge.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            Purge = "{:02}{:02}".format(hours, minutes)
        except: Purge = "0600"

        try: Effective = datetime.fromisoformat(datetime.fromisoformat(self.INFODICT.get("effective")).astimezone(timezone.utc).isoformat()).strftime("%j%H%M")
        except: Effective = datetime.now().astimezone(timezone.utc).strftime("%j%H%M")

        CALLSIGN = self.CONFIG_DATA['SAME_callsign']
        if len(CALLSIGN) > 8: CALLSIGN = "QE/2LONG"; print("[GENERATE]: Your callsign is too long!")
        elif len(CALLSIGN) < 8: CALLSIGN = "QE/2SHRT"; print("[GENERATE]: Your callsign is too short!")
        elif "-" in CALLSIGN: CALLSIGN = "QE/IVALD"; print("[GENERATE]: Your callsign contains an invalid symbol!")

        ZCZC = f"ZCZC-{ORG}-{EVE}-{LOCATION_CODES}+{Purge}-{Effective}-{CALLSIGN}-"
        ZCZC = ZCZC.replace("\n", "")
        return ZCZC

    def Generate(self):
        """ returns: dict of 'zczc', 'headline', 'text' """
        BROADCAST_TEXT = self.create_text()
        if self.CONFIG_DATA["SAME"] is True: SAME = self.create_zczc()
        else: SAME = None
        if self.Language == "FR": HEADLINE = "ALERTE D'URGENCE"
        else: HEADLINE = "EMERGENCY ALERT"
        return { "zczc":SAME, "headline":HEADLINE, "text":BROADCAST_TEXT}

class Generate_Media:
    def __init__(self, CONFIG_DATA={}, INFO_DICT={}, ALERT_DETAILS={}, ALERT_COLORS={}):
        self.config_data = CONFIG_DATA
        self.info_dict = INFO_DICT
        self.alert_details = ALERT_DETAILS
        Language = INFO_DICT.get("language")
        if "en-ca" in Language or "en-us" in Language or "en" in Language: self.Language = "EN"
        elif "fr-ca" in Language or "fr" in Language: self.Language = "FR"
        else: self.Language = "NOT_SUPPORTED"
        alert_color = ALERT_COLORS.get("background_color")
        if alert_color is None: self.alert_color = "#000000"
        else: self.alert_color = f"#{alert_color}"

    def generate_tts(self):
        audio_file_path = f"{tmp_folder}/audio.wav"
        alert_text = str(self.alert_details["text"])
        try: delete_file(audio_file_path)
        except: pass

        try:
            if self.config_data["tts_service"] == "flite":
                alert_text = alert_text.replace("\n", " ")
                subprocess.run([ "flite", "-t", alert_text, "-o", audio_file_path ], check=True)

            elif self.config_data["tts_service"] == "maki":
                alert_text = alert_text.replace("\n", " ")
                if (get_platform() == "win") and os.path.exists("./Maki.exe"):
                    app_command = "./Maki.exe"
                    if self.Language == "FR": ActiveVoice = self.config_data["maki_fr"]
                    else: ActiveVoice = self.config_data["maki_en"]
                    maki_syntax = f"{ActiveVoice}|{alert_text}|{audio_file_path}"
                    subprocess.run([ app_command, "--voice-syntax-wav", maki_syntax ], check=True)
            
            elif (self.config_data["tts_service"] == "ElevenLabs") and (elevenlabs_available is True):
                ElevenLabs_apiKey = str(self.config_data["ElevenLabs_apiKey"])
                if self.Language == "FR":
                    ElevenLabs_voiceID = self.config_data["ElevenLabs_voiceID_fr"]
                    ElevenLabs_modelID = self.config_data["ElevenLabs_modelID_fr"]
                else:
                    ElevenLabs_voiceID = self.config_data["ElevenLabs_voiceID_en"]
                    ElevenLabs_modelID = self.config_data["ElevenLabs_modelID_en"]
                client = ElevenLabs(api_key=ElevenLabs_apiKey)
                audio = client.text_to_speech.convert( text=alert_text, voice_id=ElevenLabs_voiceID, model_id=ElevenLabs_modelID, )
                save(audio, audio_file_path)
            else:
                try: pythoncom.CoInitialize()
                except: pass
                engine = pyttsx3.init()
                if self.config_data["pyttsx3_defaultTTS"] is False:
                    if self.Language == "FR": ActiveVoice = self.config_data["pyttsx3_fr"]
                    else: ActiveVoice = self.config_data["pyttsx3_en"]
                    print("[GENERATE_MEDIA]: pyttsx3 TTS using: ", ActiveVoice)
                    voices = engine.getProperty('voices')
                    ActiveVoice = next((voice for voice in voices if voice.name == ActiveVoice), None)
                    if ActiveVoice: engine.setProperty('voice', ActiveVoice.id)
                    engine.setProperty('voice', ActiveVoice)
                engine.save_to_file(alert_text, audio_file_path)
                engine.runAndWait()
        except:
            print("[GENERATE_MEDIA]: Something went wrong generating TTS. Falling back to pyttsx3 defaults.")
            try: pythoncom.CoInitialize()
            except: pass
            engine = pyttsx3.init()
            engine.save_to_file(alert_text, audio_file_path)
            engine.runAndWait()
        
    def generate_same(self):
        print("[GENERATE_MEDIA]: Generating S.A.M.E header...")
        SAMEheader = EASGen.genEAS(header=self.alert_details['zczc'], attentionTone=False, endOfMessage=False)
        SAMEeom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav(f"{tmp_folder}/same.wav", SAMEheader)
        EASGen.export_wav(f"{tmp_folder}/eom.wav", SAMEeom)

    def generate_image(self):
        final_alert_image_path = f"{tmp_folder}/alert_image.png"
        try: delete_file(final_alert_image_path)
        except: pass

        resources = self.info_dict.get("resource")
        if "image/jpeg" in str(resources): resource = get_cap_value(resources, "mimeType", "image/jpeg")
        elif "image/png" in str(resources): resource = get_cap_value(resources, "mimeType", "image/png")
        else:
            if mapGeneration_available is True:
                areas = self.info_dict.get("area")
                if isinstance(areas, dict): areas = [areas]
                polygons = []
                for area in areas: polygons.append(area.get("polygon"))
                print("polygons:", polygons)
                Generate_AlertMap(final_alert_image_path, self.alert_color, self.info_dict["headline"], polygons).generate_map()
            return None

        try: delete_file(f"{tmp_folder}/pre_image")
        except: pass

        mime_type = resource.get("mimeType")
        dref_uri = resource.get("derefUri")
        print(f"[GENERATE_MEDIA]: Image resource. {mime_type}")

        if dref_uri is not None:
            dref_uri = bytes(dref_uri, 'utf-8')
            decode = "base64"
            get_media(dref_uri, f"{tmp_folder}/pre_image", decode)
        else:
            uri = resource.get("uri")
            decode = "url_download"
            get_media(uri, f"{tmp_folder}/pre_image", decode)
        
        convert_media(f"{tmp_folder}/pre_image", final_alert_image_path)

    def generate_audio(self):
        resources = self.info_dict.get("resource")
        if "audio/mpeg" in str(resources): resource = get_cap_value(resources, "mimeType", "audio/mpeg")
        elif "audio/x-ms-wma" in str(resources): resource = get_cap_value(resources, "mimeType", "audio/x-ms-wma")
        elif "audio/wave" in str(resources): resource = get_cap_value(resources, "mimeType", "audio/wave")
        elif "audio/wav" in str(resources): resource = get_cap_value(resources, "mimeType", "audio/wav")
        elif "audio/x-ipaws-audio-mp3" in str(resources): resource = get_cap_value(resources, "mimeType", "audio/x-ipaws-audio-mp3")
        else:
            self.generate_tts()
            return None

        try: delete_file(f"{tmp_folder}/pre_audio")
        except: pass

        mime_type = resource.get("mimeType")
        dref_uri = resource.get("derefUri")
        print(f"[GENERATE_MEDIA]: Broadcast audio resource. {mime_type}")

        if dref_uri is not None:
            dref_uri = bytes(dref_uri, 'utf-8')
            decode = "base64"
            get_media(dref_uri, f"{tmp_folder}/pre_audio", decode)
        else:
            uri = resource.get("uri")
            decode = "url_download"
            get_media(uri, f"{tmp_folder}/pre_audio", decode)

        convert_media(f"{tmp_folder}/pre_audio", f"{tmp_folder}/audio.wav")

    def Generate(self):
        print("[GENERATE_MEDIA]: Generating alert media...")
        if self.config_data['SAME'] is True: self.generate_same()
        
        try: self.generate_audio()
        except: print("[GENERATE_MEDIA]: Audio generation failed!")

        if self.config_data['force_120'] is True:
            try: trim_audio(f"{tmp_folder}/audio.wav")
            except: print("[GENERATE_MEDIA]: Failed to trim broadcast audio.")

        if self.config_data['produce_alertimage'] is True:
            try: self.generate_image()
            except: print("[GENERATE_MEDIA]: Image generation failed!")

class Playout:
    def __init__(self, CONFIG_DATA={}, ALERT_REGION=None):
        if CONFIG_DATA["attn_basedoncountry"] is True:
            if "CANADA" in str(ALERT_REGION): self.attn_file = f"{assets_folder}/attns/AttnCAN.wav"
            elif "USA" in str(ALERT_REGION): self.attn_file = f"{assets_folder}/attns/AttnEBS.wav"
            else: self.attn_file = f"{assets_folder}/attns/{CONFIG_DATA["attn_tone"]}"
        else: self.attn_file = f"{assets_folder}/attns/{CONFIG_DATA["attn_tone"]}"
        self.play_pre = CONFIG_DATA["enable_leadin"]
        self.play_post = CONFIG_DATA["enable_leadout"]
        self.pre_file = f"{assets_folder}/pre.wav"
        self.post_file = f"{assets_folder}/post.wav"
        self.same_file = f"{tmp_folder}/same.wav"
        self.audio_file = f"{tmp_folder}/audio.wav"
        self.eom_file = f"{tmp_folder}/eom.wav"
        self.use_specific_audio_output = CONFIG_DATA["use_specifiedaudiooutput"]
        self.use_specific_audio_output_deviceID = CONFIG_DATA["use_audiodevice_id"]
        self.specific_audio_output = CONFIG_DATA["specifiedaudiooutput"]
    
    def playout(self, audio_file):
        time.sleep(0.5)
        if self.use_specific_audio_output is True:
            sd.default.reset()
            if self.use_specific_audio_output_deviceID is True: sd.default.device = self.specific_audio_output[0]
            else: sd.default.device = self.specific_audio_output[1]
        #sampling_rate, audio_data = wavfile.read(audio_file)
        audio_data, sampling_rate = sf.read(audio_file)
        sd.play(audio_data, samplerate=sampling_rate)
        sd.wait()

    def Play_Pre(self):
        if self.play_pre is True:
            print("[Playout]: Playing lead-in (pre-roll): ", self.pre_file)
            try: self.playout(self.pre_file)
            except: pass

    def Play_Post(self):
        if self.play_post is True:
            print("[Playout]: Playing lead-out: ", self.post_file)
            try: self.playout(self.post_file)
            except: pass

    def Play_Attn(self):
        print("[Playout]: Playing attention tone: ", self.attn_file)
        try: self.playout(self.attn_file)
        except Exception as e: print("[Playout]: Can't play attention tone! ", e)

    def Play_Audio(self):
        print("[Playout]: Playing broadcast audio")
        try: self.playout(self.audio_file)
        except Exception as e: print("[Playout]: Can't play broadcast audio! ", e)

    def Play_SAME(self):
        print("[Playout]: Playing S.A.M.E header")
        try: self.playout(self.same_file)
        except Exception as e: print("[Playout]: Can't play SAME header! ", e)

    def Play_EOM(self):
        print("[Playout]: Playing EOM header")
        try: self.playout(self.eom_file)
        except Exception as e: print("[Playout]: Can't play EOM! ", e)

# MAJOR FUNCTIONS

def Setup():
    print("[INFO]: Now setting up QuantumENDEC...")
    check_folder(history_folder, True)
    check_folder(queue_folder, True)
    check_folder(tmp_folder, True)
    check_folder("./stats", True)

    if not os.path.exists(assets_folder):
        print("[WARNING]: Could not find the assets folder! Can't function without it!")
        return False
    
    if os.path.isfile(f"{assets_folder}/config.json") is True:
        try:
            ConfigData = load_json(f"{assets_folder}/config.json")
            if ConfigData['quantumendec_version'] == QuantumENDEC_Version: pass
            else: print(f"[ATTENTION!]: Your configuration file is out of date! Go to the web interface and save (overwrite) a new one.")
        except:
            write_json(f"{assets_folder}/config.json", default_config)
    else: write_json(f"{assets_folder}/config.json", default_config)

    if os.path.isfile(f"./{assets_folder}/GeoToCLC.csv") is True: pass
    else: print("[INFO]: The GeoToCLC CSV file is missing, you don't have to worry about this if you're not using Canada's CAP and relaying in S.A.M.E. If you are using Canada's CAP and relaying in S.A.M.E, all CAP-CP alerts will have a 000000 location (FIPS/CLC) code.")

    return True

def Relay():
    update_cgen(alert_status=False)
    while True:
        try: CONFIG_DATA = load_json(f"{assets_folder}/config.json")
        except: CONFIG_DATA = default_config
        print(f"[RELAY]: Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if CONFIG_DATA["CGEN_clear_after_relay"] is True: update_cgen(alert_status=False)
        set_status("relay", "Waiting for alert")
        alert_file = watch_notify(queue_folder, history_folder) # watch notify will only pass if detected new file
        if qe_status() != 0: break
        if alert_file is None: continue
        print(f"[RELAY]: Captured alert {alert_file}")
        set_status("relay", "Processing alert...")
        AlertXML = read_file(f"{queue_folder}/{alert_file}")
        AlertDICT = xmltodict.parse(AlertXML)
        AlertDICT = AlertDICT.get("alert", {})

        # write_json("./test.json", AlertDICT) # TEST/DEBUG

        alert_sender = AlertDICT.get("sender")
        if "NAADS-Heartbeat" in alert_sender:
            print("[RELAY]: NAADS heartbeat detected")
            References = re.search(r'<references>\s*(.*?)\s*</references>', AlertXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            process_heartbeat(References, queue_folder, history_folder)
            delete_file(f"{queue_folder}/{alert_file}")
        else:
            print("[RLAY]: Alert detected")
            alert_status = AlertDICT.get("status")
            message_type = AlertDICT.get("msgType")
            alert_sent = AlertDICT.get("sent")

            if CONFIG_DATA[f"status{alert_status}"] and CONFIG_DATA[f"messagetype{message_type}"]:
                intro_played = False
                alert_region = get_alert_region(AlertDICT)

                MultipleInfoDICT = AlertDICT.get("info")
                if isinstance(MultipleInfoDICT, dict): MultipleInfoDICT = [MultipleInfoDICT]
                for InfoDICT in MultipleInfoDICT:
                    if filter_check_CAP(CONFIG_DATA, InfoDICT) is True:
                        BroadcastContent = Generate_Text(CONFIG_DATA, InfoDICT, message_type, alert_sent).Generate()
                
                        if CONFIG_DATA["SAME"] is True:
                            if not filter_check_SAME(CONFIG_DATA, BroadcastContent['zczc']): continue

                        alert_colors = get_alert_colors(CONFIG_DATA, BroadcastContent["zczc"])
                        Generate_Media(CONFIG_DATA, InfoDICT, BroadcastContent, alert_colors).Generate()

                        print(f"\n[RELAY]: NEW ALERT TO RELAY...")
                        print(BroadcastContent['headline'])
                        print(BroadcastContent['text'])
                        print("ZCZC:", BroadcastContent['zczc'])
                        set_status("relay", "Transmitting alert...")
                        Logger(CONFIG_DATA, BroadcastContent["headline"], BroadcastContent["text"], alert_colors["background_color"], "TX", BroadcastContent["zczc"]).SendLog()
                        if CONFIG_DATA["enable_plugins"] is True: run_plugins("before_relay", BroadcastContent['zczc'], BroadcastContent["text"], AlertXML, InfoDICT)
                        update_cgen(BroadcastContent["headline"], BroadcastContent["text"], alert_colors["background_color"], alert_colors["text_color"])
                        playout = Playout(CONFIG_DATA, alert_region)

                        if (CONFIG_DATA["SAME"] is True):
                            if intro_played is False:
                                playout.Play_Pre()
                                intro_played = True
                            playout.Play_SAME()
                            playout.Play_Attn()
                        else:
                            if intro_played is False:
                                playout.Play_Pre()
                                playout.Play_Attn()
                                intro_played = True

                        playout.Play_Audio()

                        if CONFIG_DATA["SAME"] is True: playout.Play_EOM()

                if intro_played is True:
                    playout.Play_Post()
                    if CONFIG_DATA["enable_plugins"] is True: run_plugins("after_relay", "", "", AlertXML, {})
                
            move_file(f"{queue_folder}/{alert_file}", f"{history_folder}/{alert_file}")

def MonitorsCaptures(CONFIG_DATA):
    """ Set up and return the threads for all Captures and Monitors """
    THREADSLIST = []

    if CONFIG_DATA["TCP_CAP"] is True:
        if CONFIG_DATA['TCP_CAP_ADDR1'] != "":
            TCPHOST, TCPPORT = CONFIG_DATA['TCP_CAP_ADDR1'].split(":")
            TCPCAP_thread = threading.Thread(target=Capture().TCP, args=(TCPHOST, TCPPORT, 1024, "</alert>", "TCP1"))
            THREADSLIST.append(TCPCAP_thread)
        
        if CONFIG_DATA['TCP_CAP_ADDR2'] != "":
            TCPHOST, TCPPORT = CONFIG_DATA['TCP_CAP_ADDR2'].split(":")
            TCPCAP_thread = threading.Thread(target=Capture().TCP, args=(TCPHOST, TCPPORT, 1024, "</alert>", "TCP2"))
            THREADSLIST.append(TCPCAP_thread)

    if CONFIG_DATA["HTTP_CAP"] is True:
        if CONFIG_DATA['HTTP_CAP_ADDR1'] != "":
            HTTPCAP_thread = threading.Thread(target=Capture().HTTP, args=(CONFIG_DATA['HTTP_CAP_ADDR1'], 1))
            THREADSLIST.append(HTTPCAP_thread)
        
        if CONFIG_DATA['HTTP_CAP_ADDR2'] != "":
            HTTPCAP_thread = threading.Thread(target=Capture().HTTP, args=(CONFIG_DATA['HTTP_CAP_ADDR2'], 2))
            THREADSLIST.append(HTTPCAP_thread)
        
        if CONFIG_DATA['HTTP_CAP_ADDR3'] != "":
            HTTPCAP_thread = threading.Thread(target=Capture().HTTP, args=(CONFIG_DATA['HTTP_CAP_ADDR3'], 3))
            THREADSLIST.append(HTTPCAP_thread)
        
        if CONFIG_DATA['HTTP_CAP_ADDR4'] != "":
            HTTPCAP_thread = threading.Thread(target=Capture().HTTP, args=(CONFIG_DATA['HTTP_CAP_ADDR4'], 4))
            THREADSLIST.append(HTTPCAP_thread)
        
        if CONFIG_DATA['HTTP_CAP_ADDR5'] != "":
            HTTPCAP_thread = threading.Thread(target=Capture().HTTP, args=(CONFIG_DATA['HTTP_CAP_ADDR5'], 5))
            THREADSLIST.append(HTTPCAP_thread)

    if ((CONFIG_DATA["NWS_CAP"]) and (CONFIG_DATA['NWS_CAP_AtomLink'] != "")):
        NWSCAPThread = threading.Thread(target=Capture().NWS, args=(CONFIG_DATA['NWS_CAP_AtomLink'],))
        THREADSLIST.append(NWSCAPThread)

    if CONFIG_DATA["SAME_AudioDevice_Monitor"] is True:
        LOCALmonitor_thread = threading.Thread(target=Monitor_Local("SAME_AudioDevice_Monitor", CONFIG_DATA).Start)
        THREADSLIST.append(LOCALmonitor_thread)

    if CONFIG_DATA["SAME_AudioStream_Monitor"] is True:
        if CONFIG_DATA["SAME_AudioStream_Monitor1"] != "":
            IPmonitor_thread = threading.Thread(target=Monitor_Stream("SAME_AudioStream_Monitor1", CONFIG_DATA["SAME_AudioStream_Monitor1"], CONFIG_DATA).Start)
            THREADSLIST.append(IPmonitor_thread)
        
        if CONFIG_DATA["SAME_AudioStream_Monitor2"] != "":
            IPmonitor_thread = threading.Thread(target=Monitor_Stream("SAME_AudioStream_Monitor2", CONFIG_DATA["SAME_AudioStream_Monitor2"], CONFIG_DATA).Start)
            THREADSLIST.append(IPmonitor_thread)
        
        if CONFIG_DATA["SAME_AudioStream_Monitor3"] != "":
            IPmonitor_thread = threading.Thread(target=Monitor_Stream("SAME_AudioStream_Monitor3", CONFIG_DATA["SAME_AudioStream_Monitor3"], CONFIG_DATA).Start)
            THREADSLIST.append(IPmonitor_thread)
        
        if CONFIG_DATA["SAME_AudioStream_Monitor4"] != "":
            IPmonitor_thread = threading.Thread(target=Monitor_Stream("SAME_AudioStream_Monitor4", CONFIG_DATA["SAME_AudioStream_Monitor4"], CONFIG_DATA).Start)
            THREADSLIST.append(IPmonitor_thread)
    
    return THREADSLIST

if __name__ == "__main__":
    set_status("QuantumENDEC", "Starting up...")
    parser = argparse.ArgumentParser(description='QuantumENDEC')
    parser.add_argument('-v', '--version', action='store_true', help='Displays QuantumENDECs version and exits.')
    parser.add_argument('-H', '--headless', action='store_true', help='Start QuantumENDEC without starting the webserver.')
    QEARGS = parser.parse_args()

    if QEARGS.version is True:
        print("QuantumENDEC", QuantumENDEC_Version)
        exit()

    print(f"-- Welcome to QuantumENDEC --\n{QuantumENDEC_Version}\n\nDevloped by ApatheticDELL alongside Aaron and BunnyTub\n")

    WebserverThread = None

    while True:
        print("Starting QuantumENDEC...")
        qe_status("set", 0)

        if Setup() is True: pass
        else:
            print("[WARNING]: Setup failed. Exiting...")
            exit()

        CONFIG_DATA = load_json(f"{assets_folder}/config.json")
        THREADSLIST = []

        if CONFIG_DATA["enable_plugins"] is True: run_plugins("on_start")

        if QEARGS.headless is False and WebserverThread is None:
            WebserverThread = threading.Thread(target=Webserver(CONFIG_DATA["webserver_host"], CONFIG_DATA["webserver_port"]).Start)
            WebserverThread.start()

        RelayThread = threading.Thread(target=Relay)
        THREADSLIST.append(RelayThread)
        MONITOR_THREADS = MonitorsCaptures(CONFIG_DATA)

        for thread in THREADSLIST: thread.start()
        for thread in MONITOR_THREADS: thread.start()
        
        set_status("QuantumENDEC", "Ready and Running")

        while qe_status() == 0:
            try: time.sleep(0.5) # keep-alive
            except KeyboardInterrupt: qe_status("set", 2)

        if qe_status() == 1:
            print("QuantumENDEC is restarting... (please wait)")
            set_status("QuantumENDEC", "Restarting... (please wait)")
        elif qe_status() == 2:
            print("QuantumENDEC is shutting down... (please wait)")
            set_status("QuantumENDEC", "Shutting down... (please wait)")

        for thread in MONITOR_THREADS: thread.join()
        for thread in THREADSLIST: thread.join()
        
        if qe_status() == 2:
            os.kill(os.getpid(), signal.SIGINT) # This is one way to do it
            exit()