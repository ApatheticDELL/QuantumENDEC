import os, time

def PlayAlert(InputConfig):
    print("Playing out alert")

    #All is playout below
    UseSpecDevice = InputConfig['UseSpecifiedAudioDevice']
    SpecDevice = InputConfig['SpecifiedAudioDevice']
    MuteV = InputConfig['MuteVirturalAudioCable']
    Vcable = InputConfig['VirturalAudioCable']

    # mute V
    if MuteV is True:
        os.system(f"pactl set-sink-mute {Vcable} 1")

    time.sleep(0.5)

    if UseSpecDevice is True:
        print("Using specified sound device with sounddevice...")
        import sounddevice as sd
        import numpy as np
        import scipy.io.wavfile as wav
        sd.default.reset()
        sd.default.device = SpecDevice
        def play(InputFile):
            file_path = InputFile
            sampling_rate, audio_data = wav.read(file_path)
            sd.play(audio_data, samplerate=sampling_rate)
            sd.wait()
    else:
        print("Using default FFPLAY")
        def play(InputFile):
            os.system(f"ffplay -hide_banner -loglevel warning -nodisp -autoexit {InputFile}")

    # play pre
    if os.path.exists("./Audio/pre.wav"):
        print("Playing Pre (Lead In) Audio")
        play("./Audio/pre.wav")

    # play same
    print("Playing SAME Tones")
    play("./Audio/same.wav")

    # play attn
    print("Playing ATTN Tone")
    play("./Audio/attn.wav")

    # play audio
    print("Playing Main Audio")
    play("./Audio/audio.wav")

    # play eom
    print("Playing EOM Tones")
    play("./Audio/eom.wav")

    # play post
    if os.path.exists("./Audio/post.wav"):
        print("Playing Post (Lead Out) Audio")
        play("./Audio/post.wav")
    
    # unmute V
    if MuteV is True:
        os.system(f"pactl set-sink-mute {Vcable} 0")