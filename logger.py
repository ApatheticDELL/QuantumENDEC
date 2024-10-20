import subprocess, smtplib
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
                    
                    if self.ConfigData["ProduceImages"] is True:
                        with open("images/alertImage.png", "rb") as f: webhook.add_file(file=f.read(), filename="image.png")

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

    def SendEmail(self, Title, Description, ZCZC, HookColor=None):
        Description = Description.replace("\n", " ")
        ZCZC = ZCZC.replace("\n", "")
        if len(ZCZC) > 1: ZCZC = f"S.A.M.E: {ZCZC}" 
        if HookColor is None or HookColor == "": HookColor = "101010"
        
        date = datetime.now()
        date = date.astimezone()
        date = date.strftime("Log: %H:%M%z %d/%m/%Y")

        style = """
            <style>
                    body {
                        background-color: #414141;
                        color: white;
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                    }
                    header {
                        background-color: """ + f"#{HookColor}" + """;
                        padding: 20px;
                        text-align: center;
                    }
                    header h1 {
                        margin: 0;
                        font-size: 2em;
                    }
                    main {
                        padding: 20px;
                    }
                    footer {
                        background-color: """ + f"#{HookColor}" + """;
                        padding: 10px;
                        text-align: center;
                        position: fixed;
                        width: 100%;
                        bottom: 0;
                    }
            </style>
        """

        body = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>QuantumENDEC Email Log</title>
                {style}
            </head>
            <body>
                <header>
                    <h1>QuantumENDEC Email Log</h1>
                </header>

                <main>
                    <h2>{Title}</h2>
                    <p>{Description}</p>
                    <p>{ZCZC}</p>
                </main>

                <footer>
                    <p>QuantumENDEC - {date}</p>
                </footer>
            </body>
        </html>
        """

        message = MIMEMultipart()
        message["From"] = self.ConfigData["email_user"]
        message["Subject"] = f"QuantumENDEC: {Title} - {date}"
        if(type(self.ConfigData["email_sendto"]) == list): message['To'] = ",".join(self.ConfigData["email_sendto"])
        else: message['To'] = self.ConfigData["email_sendto"]

        if self.ConfigData["FancyHTML"] is True:    
            thing = MIMEText(body, 'html')
            message.attach(thing)
        else:
            basic_text = f"QuantumENDEC... {Title}\n{Description}\n{ZCZC}"
            thing = MIMEText(basic_text, 'plain')
            message.attach(thing)

        mail = smtplib.SMTP(self.ConfigData['email_server'], int(self.ConfigData['email_server_port']))
        mail.ehlo()
        mail.starttls()
        mail.login(self.ConfigData["email_user"], self.ConfigData["email_user_pass"])
        mail.sendmail(self.ConfigData["email_user"], self.ConfigData["email_sendto"], message.as_string())
        mail.quit()

    def TxtLog(self, Title, Description, ZCZC):
        dateNow = datetime.now().strftime("%B %d, %Y %H:%M:%S")
        if ZCZC == "": log = f"{Title}\n{Description}"
        else: log = f"{Title}\n{Description}\n{ZCZC}"
        log = f"\n--- {dateNow} ---\n{log}\n"
        try:
            with open("alertlog.txt", "a", encoding='utf-8') as f: f.write(log)
        except:
            with open("alertlog.txt", "w", encoding='utf-8') as f: f.write(log)

    def SendLog(self, Title, Description, ZCZC, type="", HookColor=None):
        if self.ConfigData['enable_discord_webhook'] is True:
            print("Sending Discord webhook...")
            try: self.SendDiscord(Title, Description, ZCZC, type, HookColor)
            except: print("Discord, failed to log.")

        if self.ConfigData['enable_LogToTxt'] is True:
            print("Logging to alertlog.txt...")
            try: self.TxtLog(Title, Description, ZCZC)
            except: print("Text file, failed to log.")

        if self.ConfigData['enable_email'] is True:
            print("Logging to email...")
            try: self.SendEmail(Title, Description, ZCZC, HookColor)
            except: print("Email, failed to log,")

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