import requests

url = "http://localhost:8000/api/predict/wav"
with open("test_audio.wav", "rb") as f:
    resp = requests.post(url, files={"file": ("test_audio.wav", f, "audio/wav")})

print("Status:", resp.status_code)
print("Body:", resp.json())
