
# Twitch AI Dungeon 

Allow Twitch chat to play AI Dungeon

## Website

The website in question is https://play.aidungeon.io/.<br>
Initially, you are asked to enter an email address, and are prompted to make an account. This account seems to be used to save and return to specific stories.<br>
This login is cached, so returning to the website after logging in once does not require you to log in again.<br>

### Starting
It's possible to create a new story by sending roughly<br>
```json
{
    "storyMode":"fantasy",
    "characterType":"rogue",
    "name":"Bob",
    "customPrompt":null,
    "promptId":null
}
```

to https://api.aidungeon.io/sessions, using a POST request. Note that this is very similar to what's described in the Sessions section. The main difference seems to be the lack of any json sent along in that case.<br>
There are several possible story modes, and each story modes has several possible character types. Perhaps the name could be voted on by chat, could simply be `CubieB0T`, or could be changed as a channel points reward (It seems like there is a simple way to change a user's name mid-adventure).

### Responses
Your responses are sent as simple unencrypted json via POST to the server, which returns a list of all data so far. This list includes what you've typed, as well as what the server has responded with.<br>
We can somewhat easily bypass all the frontend stuff, and send POST requests to the backend server at api.aidungeon.io.<br>
<br>
To get a successful POST request, we seem to need two things:
* An `X-Access-Token`.
* A session id.

The former is passed as a header, while the latter is related to the session your game is.<br>
For the time being I have copied both of these values directly from an active session I played on my browser.<br>

### Sessions
The API seems to have an endpoint called `sessions` (https://api.aidungeon.io/sessions) which sends back a list of all games you've played. Within this information is the session id of these games. <br>
Given our `X-Access-Token`, we can extract the session id.<br>
<br>
Now we just need to either: Be sure that our `X-Access-Token` never changes, or find some way to generate a new one on the spot.

## Goals
Primary Goal:<br>
`Allow chat to interact with, and play, AI Dungeon`.<br>
Subgoals: 
* Allow moderators to restart games
* Implement filters to avoid NSFW situations
  * Note that AI Dungeon 2 itself has a NSFW filter which seems to help, but does not remove all NSFW cases. Perhaps it's simply less graphic. By default this filter is on.
* Create chat aliases for special commands. 
  * `/reminder <text>` to have the AI remember story details. In chat this could be `!remember <text>`.
  * `/revert` will revert your last action. In chat this could be `!revert`.
  * `"<text>"` to talk rather than do. In chat this could be `!say <text>`.
  * `!<event>` to have an event occur. In chat this could be `!event <text>`.
  * Normal sentences are actions. In chat this could be `!do <text>`.
  * Note that not all of these will actually give output. For instance, `/remember` does not appear to.
* Implement a command explaining all possible commands. Perhaps also incentivise people to write long and convoluted instructions.
* Some responses include us giving responses. We need to find a way to format this nicely for Twitch chat. Some possibilities
  * Use "⠀". This is a space with unusual width, which are no longer filtered out by Twitch, unlike normal subsequent spaces, ever since the font changes were introduced. We can use this to space-pad sentences to a specific length, to force subsequent sentences to start on a new line. Essentially we can use this to create a newline.
  * Simply concatenate everything by removing the `\n`'s and `>`'s, and use different quotation marks for sentences spoken by us.
  * I prefer the first method, but we might hit the character limit on responses that way, as the spaces will count as characters. I don't know what the Twitch character limit is, nor do I know what the limit of response length from AI Dungeon is.
  * Eg this is one response:
```
> You tell her about the man.
Lisa looks at you and smiles. She says "Heh, he is indeed a nice fellow. He saved me from an orc attack once."
> You ask her some questions about him.
"So...what do you do now?"
```

## Difficulties
* What if someone wasn't there at the start of the adventure? Or what if they missed a part? How would they catch up? 
* Would people be interested in playing an adventure if it cannot be spammy in chat? If it's launched on MALF's channel, he would propose a 60s+ cooldown I'm sure. 
* Potentially having to refresh or update the `X-Access-Token`. 
* Filtering out NSFW, unwanted situations.

## Tasks

- [ ] Manage to take advantage of the API to send messages to AI Dungeon.
  - [x] Send and receive messages.
  - [ ] Start and restart adventures.
  - [ ] (Potentially) Refresh the `X-Access-Token`.
- [ ] Parse the output from the AI Dungeon 2 API to a format viable for Twitch chat.
- [ ] Use my `TwitchWebsocket` to create a simple bot which tasks the aforementioned to request the API.
  - [ ] Implement all commands.
  - [ ] Implement a NSFW filter.
