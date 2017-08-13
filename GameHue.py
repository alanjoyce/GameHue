import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning,SNIMissingWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

# Import config
config = {}
f = open('config.txt', 'r')
for line in f:
  if line[0] == ":":
    linePieces = line.split()
    config[linePieces[1]] = linePieces[2]

# Look for a Steam game
r = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + config["steam_key"] + "&steamids=" + config["steam_user"])
json_data = r.json()
gameID = json_data["response"]["players"][0].get("gameid")
if gameID is not None:
  gameImage = "http://cdn.akamai.steamstatic.com/steam/apps/" + gameID + "/header.jpg"
  print "Found a Steam game: " + gameImage
else:
  gameImage = None

# If we didn't find a Steam game, look for an Xbox game
if gameImage is None:
  headers = {'X-AUTH': config["xbox_key"]}
  r = requests.get("https://xboxapi.com/v2/" + config["xbox_user"] + "/presence", headers=headers, verify=False)
  json_data = r.json()
  devices = json_data.get("devices")
  if devices is not None and len(devices) > 0:
    deviceTitles = devices[0]["titles"]
    if len(deviceTitles) > 1:
      gameID = hex(deviceTitles[1]["id"])[2:]
      r = requests.get("https://xboxapi.com/v2/game-details-hex/" + gameID, headers=headers, verify=False)
      json_data = r.json()
      gameImage = json_data["Items"][0]["Images"][0]["Url"]
      print "Found an Xbox game: " + gameImage

# TODO: If we didn't find an Xbox game, look for a PlayStation game
# Right now, we never find any PlayStation games because there's no API

# If we didn't find any game, then we shouldn't do anything else
if gameImage is None:
  # Clear the lastgame file to reflect current state
  open('lastgame.txt', 'w').close()
  print "No games found."
  exit()

# Record the found game and check if it's the same as before
f = open('lastgame.txt', 'r')
lastGame = f.readline()
f.close()
if lastGame == gameImage + "\n":
  print "The found game was the same game as last time. Skipping."
  exit()
else:
  # Clear the file before updating it
  open('lastgame.txt', 'w').close()

# Import color overrides
dominantColors = []
f = open('overrides.txt', 'r')
for line in f:
  linePieces = line.split()
  if gameID == linePieces[0]:
    dominantColors.append(linePieces[1])
    dominantColors.append(linePieces[2])
    dominantColors.append(linePieces[3])
f.close()
  
# Keep a record of the new game
f = open('lastgame.txt', 'w')
f.write(gameImage + "\n")

# If we don't have a color override, dynamically find colors
if len(dominantColors) == 0:
  # Use Google Cloud Vision API to check colors
  data = {"requests": [{"image": {"source": {"imageUri": gameImage}},"features": [{"type": "IMAGE_PROPERTIES","maxResults": 1}]}]}
  r = requests.post("https://vision.googleapis.com/v1/images:annotate?fields=responses%2FimagePropertiesAnnotation&key=" + config["google_key"], json=data)
  json_data = r.json()
  
  # Loop through returned colors and grab the dominant ones
  i = 0
  for color in json_data["responses"][0]["imagePropertiesAnnotation"]["dominantColors"]["colors"][0:3]:
    red = color["color"]["red"]
    green = color["color"]["green"]
    blue = color["color"]["blue"]
    f.write("\nFound color: " + str(red) + " red, " + str(green) + " green, " + str(blue) + " blue")
    
    # Use a scaling factor to make things brighter if needed
    scale = 255.0/float(max(red,green,blue))
    
    # Use a lower scaling factor for non-primary/non-secondary colors
    if i > 1:
      scale = 1.0
    
    red = min(255, int(red * scale))
    green = min(255, int(green * scale))
    blue = min(255, int(blue * scale))
    f.write("\nIntensified color: " + str(red) + " red, " + str(green) + " green, " + str(blue) + " blue")
    hexColor = '#%02x%02x%02x' % (red, green, blue)
    dominantColors.append(hexColor)
    i = i + 1

primaryColor = dominantColors[0]
secondaryColor = dominantColors[1]
tertiaryColor = dominantColors[2]
f.close()

print "This is a new game! Colors:"
print "Primary \t" + primaryColor
print "Secondary \t" + secondaryColor
print "Tertiary \t" + tertiaryColor

# Make some IFTTT calls
data = {"value1":primaryColor}
r = requests.post("https://maker.ifttt.com/trigger/hue_primary/with/key/" + config["ifttt_key"], json=data)

data = {"value1":secondaryColor}
r = requests.post("https://maker.ifttt.com/trigger/hue_secondary/with/key/" + config["ifttt_key"], json=data)

data = {"value1":tertiaryColor}
r = requests.post("https://maker.ifttt.com/trigger/hue_tertiary/with/key/" + config["ifttt_key"], json=data)

print "All colors sent to IFTTT. Light changes should be imminent."


