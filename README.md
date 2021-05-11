# TwitchAIDungeon
Twitch Bot allowing chat to play [AI Dungeon 2](https://play.aidungeon.io/).

---

# Important

The AI Dungeon API has changed since the creation of this project, and as a result **it no longer works!**
I'm unable to prioritize this project right now, but I'll leave it un-archived as I'm open to changes, and might have the time to revisit this project in the future.
 
--- 
# Explanation

When the bot has started, it will start listening to chat messages in the channel listed in the `settings.json` file. Whenever a chat member uses one of the accepted commands, the bot will forward the action to [AI Dungeon 2](https://play.aidungeon.io/), a procedurally generated text-based adventure game, and post the result of their action in Twitch chat. This way, Twitch chat will be able to play AI Dungeon 2.

Due to the potential NSFW nature of AI Dungeon 2, it is possible to pass a blacklist to the bot. This way, inputs containing a banned word or phrase will not be sent to AI Dungeon 2, and outputs containing a banned word or phrase will be censored with stars. See [Blacklist](#blacklist) for more information.

Furthermore, there is a configurable cooldown between actions to prevent spam. See [Settings](#settings) for more information.

---

### Notes
- AI Dungeon 2 is often overloaded, and responds slowly to messages. As a result, so will the bot. It may take several seconds for the bot to respond.<br>
- AI Dungeon 2 sometimes seems to ignore the action you take in favour of continuing storyline.
  - This seems to be more common the more actions have been taken. At that point its best to restart the adventure.

---
# Commands
Chat members can perform actions in AI Dungeon 2 by using the following commands:
| *Command* | *Example* | *Use* |
| - | - | - |
| `!do [action]` | `!do detonate the planet venus using the death star`| Actions we take. |
| `!event [event]` | `!event suddenly your mother in law shows up` | Actions not performed by us. |
| `!say [message]` | `!say do you smell that?` | Whenever we want to speak. |
| `!remember [fact]` | `!remember my name is Bot` | Whenever we want to remember a fact. |
| `!revert` | `!revert` | To undo the previous command. |
| `!help` | `!help` | To make the bot say a help message with these commands. |
| `!restart` | `!restart` | To restart the adventure. Only people with the allowed ranks can do this. See [Settings](#settings) for the allowed ranks. |

---

# Settings
This bot is controlled by a `settings.json` file, which looks like:
```json
{
    "Host": "irc.chat.twitch.tv",
    "Port": 6667,
    "Channel": "#<channel>",
    "Nickname": "<name>",
    "Authentication": "oauth:<auth>",
    "Cooldown": 20,
    "X-Access-Token": "<accessToken>",
    "AllowedRanks": [
        "broadcaster",
        "moderator",
        "vip"
    ],
    "AllowedUsers": [],
    "CustomPrompt": "You are Bot, a wizard living in the kingdom of Larion. You have a staff and a spellbook. You finish your long journey and finally arrive at the ruin you've been looking for. You look around and see that it's not much different than when you left it. A few more trees here and there, but nothing has changed."
}
```

| **Parameter**        | **Meaning** | **Example** |
| -------------------- | ----------- | ----------- |
| Host                 | The URL that will be used. Do not change.                         | "irc.chat.twitch.tv" |
| Port                 | The Port that will be used. Do not change.                        | 6667 |
| Channel              | The Channel that will be connected to.                            | "#CubieDev" |
| Nickname             | The Username of the bot account.                                  | "CubieB0T" |
| Authentication       | The OAuth token for the bot account.                              | "oauth:pivogip8ybletucqdz4pkhag6itbax" |
| Cooldown | A cooldown in seconds between actions. When a user hits this cooldown, they will be whispered the time remaining until the cooldown expires. Users can opt out of this whispering. | 20 |
| X-Access-Token | The access token for your AI Dungeon Login. | "zhk4v79g2-m6t6-6f06-6hqd-qc5pdyfp1yx3" |
| AllowedRanks | The ranks for people need to have to be able to use !restart. | ["broadcaster", "vip", "moderator" ] |
| CustomPrompt | The starting prompt with which adventures are started. | "You are Bot, a wizard living in the kingdom of Larion. ..." | 

*Note that the example OAuth token and X-Access-Token are not actual tokens, but merely generated strings to give an indication what they might look like.*

I got my real OAuth token from https://twitchapps.com/tmi/.

---

### X-Access-Token

Getting the X-Access-Token is slightly more involved. Note that I'm doing these steps on Firefox, though the steps should be similar on other browsers:
- Browse to https://play.aidungeon.io/ and log in.
  - Optionally make an account if you dont have one already.
- Press F12 to open the developer tools.
- Go to the Storage tab.
- Go to the Local Storage tab.
- Browse through the options until you see `LOGGED_IN_USER`.
- Click on the corresponding value, and look for "accessToken".
- Copy the value there, which is likely along the likes of "zhk4v79g2-m6t6-6f06-6hqd-qc5pdyfp1yx3", and use it as your value for X-Access-Token.

---

# Blacklist

The `blacklist.txt` file can be filled with banned words or phrases, each oh a new line. A sample blacklist is the this [censored_words.txt](https://github.com/AIDungeon/AIDungeon/pull/235/files) by [Teravus](https://github.com/Teravus). It is recommended for this file to be sorted such that longer phrases appear at the top of the file, however this is not a requirement.

---

# Requirements
* [Python 3.6+](https://www.python.org/downloads/)
* [Module requirements](requirements.txt)<br>
Install these modules using `pip install -r requirements.txt` in the commandline.

Among these modules is my own [TwitchWebsocket](https://github.com/CubieDev/TwitchWebsocket) wrapper, which makes making a Twitch chat bot a lot easier.
This repository can be seen as an implementation using this wrapper.

---

# Other Twitch Bots

* [TwitchMarkovChain](https://github.com/CubieDev/TwitchMarkovChain)
* [TwitchAIDungeon](https://github.com/CubieDev/TwitchAIDungeon)
* [TwitchGoogleTranslate](https://github.com/CubieDev/TwitchGoogleTranslate)
* [TwitchCubieBotGUI](https://github.com/CubieDev/TwitchCubieBotGUI)
* [TwitchCubieBot](https://github.com/CubieDev/TwitchCubieBot)
* [TwitchRandomRecipe](https://github.com/CubieDev/TwitchRandomRecipe)
* [TwitchUrbanDictionary](https://github.com/CubieDev/TwitchUrbanDictionary)
* [TwitchRhymeBot](https://github.com/CubieDev/TwitchRhymeBot)
* [TwitchWeather](https://github.com/CubieDev/TwitchWeather)
* [TwitchDeathCounter](https://github.com/CubieDev/TwitchDeathCounter)
* [TwitchSuggestDinner](https://github.com/CubieDev/TwitchSuggestDinner)
* [TwitchPickUser](https://github.com/CubieDev/TwitchPickUser)
* [TwitchSaveMessages](https://github.com/CubieDev/TwitchSaveMessages)
* [TwitchMMLevelPickerGUI](https://github.com/CubieDev/TwitchMMLevelPickerGUI) (Mario Maker 2 specific bot)
* [TwitchMMLevelQueueGUI](https://github.com/CubieDev/TwitchMMLevelQueueGUI) (Mario Maker 2 specific bot)
* [TwitchPackCounter](https://github.com/CubieDev/TwitchPackCounter) (Streamer specific bot)
* [TwitchDialCheck](https://github.com/CubieDev/TwitchDialCheck) (Streamer specific bot)
* [TwitchSendMessage](https://github.com/CubieDev/TwitchSendMessage) (Meant for debugging purposes)

