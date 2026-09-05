import requests
import json

API_KEY = "730340d81037e2fe050d60dccbb41c16"
USER_ID = "160043453@N06"
PHOTOSET_ID = "72177720318432668"

url = (
    "https://api.flickr.com/services/rest/?"
    f"method=flickr.photosets.getPhotos&api_key={API_KEY}"
    f"&photoset_id={PHOTOSET_ID}&user_id={USER_ID}"
    "&extras=url_s,url_m,url_o"
    "&format=json&nojsoncallback=1"
)

resp = requests.get(url)
data = resp.json()

with open("album.json", "w") as f:
    json.dump(data, f, indent=2)

print("Album JSON saved successfully!")