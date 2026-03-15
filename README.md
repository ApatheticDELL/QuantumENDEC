ApatheticDELL presents...

# QDEC v5

## Credits

### Developed by
```
Dell --- https://apatheticdell.net/
Aaron --- https://secludedfox.com/
BunnyTub --- https://bunnytub.com/
```
### Additional Assistance
```
AC --- ac22real
Midland --- midlandwr100
```
Generative AI was used in the making of QDEC.

------------------------------------------------------------------------

## Description

**QDEC** is a Python-based emergency alerting system capable of monitoring and processing alerts from multiple sources, including:

-   Canadian **NAADS** feeds (CAP-CP)
-   American **CAP** feeds (NWS ATOM or IPAWS Open)
-   **S.A.M.E.** audio inputs

QDEC was previously known as **QuantumENDEC** before June 21, 2025.

------------------------------------------------------------------------

## Installation

Installing QDEC is straightforward, but some external software is required.

> [!CAUTION]
> QDEC must run on a system with at least one audio output device.\
> It will **not** function correctly in browser-based or online environments (such as github.dev).

### Required Software

-   Python (3.13 or newer) - https://www.python.org/
-   FFmpeg - https://ffmpeg.org/

### Optional Software

-   multimon-ng - https://github.com/EliasOenal/multimon-ng/ \
    Required on Linux when using SAME monitoring features.\
    (Windows binary already included.)

-   Microsoft Visual C++ Redistributable -
    https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist/ \
    Required for map generation on Windows.

------------------------------------------------------------------------

## Text-to-Speech (TTS)

At least one TTS engine must be installed.

Supported engines:

-   eSpeak NG (default) - Windows & Linux
-   Piper - Windows & Linux
-   flite - Linux
-   Maki - Windows only
-   ElevenLabs - Web API

### TTS Notes

**Piper** - Place the Piper folder in the QDEC root directory. - Voices and JSON files go inside: /piper_voices

**Maki** - Windows only. - Binary already included. - Supports 32‑bit and 64‑bit voices.

**ElevenLabs** - Installed automatically via Python requirements. Requires an API key.

------------------------------------------------------------------------

## Python Dependencies

Install all dependencies:
```
py -m pip install -r requirements.txt
```
Run this inside the QDEC root directory.

------------------------------------------------------------------------

## Setup

Some familiarity with Pelmorex CAP‑CP is recommended for NAADS feeds:

https://alerts.pelmorex.com/wp-content/uploads/2021/06/NAADS-LMD-User-Guide-R10.0.pdf

(Not required for SAME-only setups.)

### Starting QDEC

Run: 
```
py QDEC.py
```
> [!IMPORTANT]
> Your system may use `python` or `python3` instead of `py`.

The web interface will start on port **5000**.

Open:

    http://localhost:5000

or:

    http://<device-ip>:5000

------------------------------------------------------------------------

### Default Login

Default password:
```
hackme
```
> [!WARNING] 
> It is **highly recommended** to change this immediately after first login. Running QDEC with its default password is a major security risk.
> ### To change your password:
> Go to the Change Access Password tab, enter your new password, and hit Change Password to finish. You will then be logged out, and must use your new password to log in.

------------------------------------------------------------------------

## Configuration

After logging in:

1.  Open the Configuration tab.
2.  Enable desired alert sources.
3.  Configure filters and integrations.

Features include:

-   Discord webhook integration
-   Alert status filtering
-   Severity & urgency filtering
-   Geographic filtering

All monitoring sources are disabled by default.

Some changes require restarting QDEC.

------------------------------------------------------------------------

### Geographic Filtering

Filtering uses:

-   SAME CLC codes
-   CAP‑CP Geocodes

#### Province Example

-   SAME CLC: 04 (Ontario)
-   CAP‑CP: 35\*

#### Region Example

-   SAME CLC: 0466 (Halton--Peel)
-   CAP‑CP: 3521 or 3521\*

Location references:

-   SAME CLC: https://en.wikipedia.org/wiki/Forecast_region
-   CAP‑CP codes:
    https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/capcp-lctn-rfrncs/index4-en.aspx

Press **Save** after configuration.

------------------------------------------------------------------------

## Command-Line Arguments

View options:
```
py QDEC.py -h
```

------------------------------------------------------------------------

## Disclaimer

Emergency information is sourced from official providers, but QDEC should not be relied upon as a sole emergency information source.

------------------------------------------------------------------------

## Acknowledgements

Even though this was coded from (mostly) the ground up, I'd still like to credit Libmarleu's BashENDEC (which no longer exists on their page) for starting the QDEC journey in 2021.

And thanks to all who worked on this one, hell of an ENDEC...
