import sounddevice as sd

print(sd.query_devices())
print("")
print("This is a list of audio output devices alert audio is able to output to! To select a device, copy its name into the SpecifiedAudioDevice feild in the config.json")

exit()