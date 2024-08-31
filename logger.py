from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import subprocess

class Log:
    def __init__(self, ConfigData):
        self.ConfigData = ConfigData

    def SendDiscord(self, Title, Description, ZCZC, type="", HookColor=None):
        Wauthorname = self.ConfigData['webhook_author_name']
        Wauthorurl = self.ConfigData['webhook_author_URL']
        Wiconurl = self.ConfigData['webhook_author_iconURL']
        Wurl = self.ConfigData['webhook_URL']
        Description = Description.replace("/n", " ")
        if len(Description) > 2000: Description = f"{Description[:2000]}..."
        if len(ZCZC) > 1000: ZCZC = f"{ZCZC[:1000]}..."
        webhook = DiscordWebhook(url=Wurl, rate_limit_retry=True)
        
        # Send audio
        if type == "TX":
            if self.ConfigData['webhook_sendAudio'] is True:
                try:
                    subprocess.run(["ffmpeg", "-y", "-i", "Audio/audio.wav", "-map", "0:a:0", "-b:a", "64k", "Audio/tmp/DiskAudio.mp3"], capture_output=True, text=True)
                    with open("Audio/tmp/DiskAudio.mp3", "rb") as f: webhook.add_file(file=f.read(), filename="audio.mp3")
                except: pass

        if HookColor is None or HookColor == "": Wcolor = "ffffff"
        else: Wcolor = HookColor
        
        embed = DiscordEmbed(title=Title, description=Description, color=Wcolor,)
        if ZCZC == "": pass
        else: 
            ZCZC = f"```{ZCZC}```"
            embed.add_embed_field(name="", value=ZCZC, inline=False)
        embed.set_author(name=Wauthorname, url=Wauthorurl, icon_url=Wiconurl)
        embed.set_footer(text="Powered by QuantumENDEC")
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()

    def TxtLog(self, Title, Description, ZCZC):
        dateNow = datetime.now().strftime("%B %d, %Y %H:%M:%S")
        if ZCZC == "": log = f"{Title}\n{Description}"
        else: log = f"{Title}\n{Description}\n{ZCZC}"
        log = f"\n--- {dateNow} ---\n{log}\n"
        try:
            with open("alertlog.txt", "a") as f: f.write(log)
        except:
            with open("alertlog.txt", "w") as f: f.write(log)

    def SendLog(self, Title, Description, ZCZC, type="", HookColor=None):
        if self.ConfigData['enable_discord_webhook'] is True:
            print("Sending Discord webhook...")
            try: self.SendDiscord(Title, Description, ZCZC, type, HookColor)
            except: print("Discord, failed to log.")

        if self.ConfigData['enable_LogToTxt'] is True:
            print("Logging to alertlog.txt...")
            try: self.TxtLog(Title, Description, ZCZC)
            except: print("Text file, failed to log.")

        print("Finished logging.")


# Typical recv log:
# Title: Emergency Alert Received
# Headline: Receipt:
# Description: Received at {date} from {monitorName}
# ZCZC: {SAMEheaderSource}

# Typical send log:
# Title: Emergency Alert Transmission
# Headline: EMERGENCY ALERT // ALERT'D URGE FRENCH
# Description: {BroadcastText}
# ZCZC: {SAMEheaderOutput}

# Standard Canada EAS message can be max 1800 chars.