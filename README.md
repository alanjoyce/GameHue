# GameHue
Automatically change Hue lights to match the poster art of the game you're currently playing.

# Configuration

Open config.txt and set the following values:

* **google_key** should be a Google Cloud API key with the Cloud Vision API enabled. See https://cloud.google.com/vision/.
* **xbox_key** should be an API key from https://xboxapi.com/. Note: You will need to tell Xbox API to "remember me" if you don't want to sign into your Xbox account there every day.
* **xbox_user** is your Xbox Profile User ID. You can find this on your profile page at https://xboxapi.com/.
* **steam_key** should be a Steam Web API key. See https://steamcommunity.com/dev.
* **steam_user** is your Steam user ID. You can use http://steamidfinder.com/ to find this easily (you want the "steamID64").
* **ifttt_key** should be a key from the IFTTT webhooks service. See https://ifttt.com/maker_webhooks and click on "Documentation" in the upper-right to see your key.

# Usage

Just run:

    python GameHue.py

The script will check if you are playing a game on Steam, then do the same for Xbox. PlayStation is not working at the moment. If it finds a game, it will send the banner image for that game to the Google Cloud Vision API, retrieve the dominant colors, and then fire off three intents to your IFTTT webhook:
* **hue_primary** will include the most dominant color as Value1
* **hue_secondary** will include the second-most dominant color as Value1
* **hue_tertiary** will include the third-most dominant color as Value1

You can configure IFTTT to do whatever you'd like in response to these webhooks, but the intent is that you set it to change various lights in your home to the primary/secondary/tertiary colors.

You may also want to set up a cron job to run this script every minute or so. With that cadence, your lights will typically change before most games have finished loading. Magical!

Have fun!
