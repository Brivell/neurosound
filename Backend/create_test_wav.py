import wave, struct, math, os

sample_rate = 16000
duration = 5
freq = 440
num_samples = sample_rate * duration

with wave.open("test_audio.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sample_rate)
    for i in range(num_samples):
        value = int(32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        f.writeframes(struct.pack("<h", value))

print("Created test_audio.wav,", os.path.getsize("test_audio.wav"), "bytes")
