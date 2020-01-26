
import time, logging

from Settings import Settings
from Log import Log
Log(__file__, Settings.get_channel())
Settings.set_logger()

from TwitchWebsocket import TwitchWebsocket
from Database import Database
from api import API

class TwitchAIDungeon:
    def __init__(self):
        # Initialize variables to None
        self.host = None
        self.port = None
        self.chan = None
        self.nick = None
        self.auth = None
        capability = []
        self.access_token = None
        self.cooldown = 0
        self.last_command_time = 0

        # Create an Api instance to connect to AI Dungeon 2.
        logging.debug("Creating API instance.")
        self.api = API(self)

        # Update variables
        logging.debug("Setting settings.")
        Settings(self)

        # Create a Database instance for storing which users do not want to be whispered
        logging.debug("Creating Database instance.")
        self.db = Database(self.chan)

        # Get the session_id
        self.session_id = self.api.get_session_id()

        # Create Websocket object
        logging.debug("Creating TwitchWebsocket object.")
        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=capability,
                                  live=True)
        # Start a blocking websocket connection
        logging.debug("Starting Websocket connection.")
        self.ws.start_bot()

    def set_settings(self, host, port, chan, nick, auth, cooldown, access_token):
        self.host, self.port, self.chan, self.nick, self.auth, self.cooldown, self.access_token = host, port, chan, nick, auth, cooldown, access_token

    def message_handler(self, m):
        #print(m)
        if m.type == "PRIVMSG":
            #if m.message.startswith("hello"):
            #    out = '> \nShe points to a spot on the wall. "There, there\'s a little alcove behind that lock. There you can find the key."\n> You agree to help her unlock it.\n"I\'ll get back to you as soon as I can."'
            #    out = self.parse_output(out)
            #    self.ws.send_message(out)
            if m.message.startswith("!do"):
                self.command_do(m)
            elif m.message.startswith("!remember"):
                self.command_remember(m)
            elif m.message.startswith("!revert"):
                self.command_revert(m)
            elif m.message.startswith("!event"):
                self.command_event(m)
            elif m.message.startswith(("!say", "!talk", "!ask")):
                self.command_say(m)

    def extract_message(self, m):
        try:
            # Extract the message after the first space.
            return m.message[m.message.index(" ") + 1:]
        except ValueError:
            # If no spaces, return empty string
            return ""

    def check_cooldown(self):
        # True iff it has been `self.cooldown` seconds since the last command use.
        return self.last_command_time + self.cooldown < time.time()

    def check_cooldown(self, m):
        # Difference is the amount of seconds remaining on the cooldown
        difference = self.last_command_time + self.cooldown - time.time()
        if difference <= 0:
            return True
        # If the cooldown has been hit, and the user has not said they don't want to be whispered, then whisper them the cooldown.
        if not self.db.check_whisper_ignore(m.user):
            self.ws.send_whisper(m.user, f"Cooldown hit: {difference:.2f} out of {self.cooldown:.0f}s remaining. !nopm to stop these cooldown pm's.")
        return False

    def command_action(self, message, prefix="", postfix="", custom_output="", force=False):
        # If force is True, then we will communicate with the API even if the message is empty.

        # Function to handle communication between API and this class
        if message or force:
            # Set the last_command_time to the current time for cooldown
            self.last_command_time = time.time()

            logging.debug(f"Calling api.say with \"{prefix + message + postfix}\"")
            out = self.api.say(prefix + message + postfix)
            out = self.parse_output(out)
            # If a custom output is warranted for this action type, use that as output instead
            if custom_output:
                out = custom_output
        else:
            out = "Please also enter a message alongside your command."
        
        if out:
            logging.info(f"Chat output: {out}")
            self.ws.send_message(out)

        else:
            out = "AI Dungeon 2 responded with an empty message, sadly."
            logging.error(out)
            self.ws.send_message(out)

    def command_do(self, m):
        if self.check_cooldown(m):
            # Force is True for `!do`, as an empty message will allow more dialoge to generate on its own
            self.command_action(self.extract_message(m), force=True)

    def command_remember(self, m):
        if self.check_cooldown(m):
            message = self.extract_message(m)
            self.command_action(message, prefix="/remember ", custom_output=f"Added \"{message}\" to game's memory.")

    def command_revert(self, m):
        # Note that reverting is not affected by the cooldown and can be done whenever.
        # TODO: Add a short cooldown to prevent two people from reverting at once, and reverting twice.
        self.command_action("/revert", custom_output=f"The last action has been reverted.")

    def command_event(self, m):
        if self.check_cooldown(m):
            self.command_action(self.extract_message(m), prefix="!")

    def command_say(self, m):
        if self.check_cooldown(m):
            self.command_action(self.extract_message(m), prefix="\"", postfix="\"")

    def parse_output(self, message):
        # TODO: Improve upon this. 
        # Make it so conversations with different perspectives are clearly separated.
        return message.replace("\n", " ")

if __name__ == "__main__":
    TwitchAIDungeon()

"""
TODO: 
- Start and Restart adventures. Perhaps allow switching between adventures, as they are already stored on AI Dungeon.
- Convert the output to a more readable format, when different perspectives are involved.
- NSFW filter

Actions, request method and api endpoint
Session ID:     GET     https://api.aidungeon.io/sessions
Delete Story:   DELETE  https://api.aidungeon.io/sessions/<id>
Create Story:   POST    https://api.aidungeon.io/sessions
Talk:           POST    https://api.aidungeon.io/inputs/<id>

Possible output:
"> 
She points to a spot on the wall. "There, there's a little alcove behind that lock. There you can find the key."
> You agree to help her unlock it.
"I'll get back to you as soon as I can.""
"""
