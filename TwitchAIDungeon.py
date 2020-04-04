
import time, logging, threading

from Settings import Settings
from Log import Log
Log(__file__, Settings.get_channel())
Settings.set_logger()

from TwitchWebsocket import TwitchWebsocket
from Database import Database
from API import API

from profanityfilter import ProfanityFilter

class TwitchAIDungeon:
    def __init__(self):
        # Initialize variables to None
        self.host = None
        self.port = None
        self.chan = None
        self.nick = None
        self.auth = None
        capability = ["tags"]
        self.access_token = None
        self.cooldown = 0
        self.last_command_time = 0
        self.allowed_ranks = []
        self.allowed_users = []
        self.custom_prompt = ""
        with open("blacklist.txt", "r") as f:
            censor = [l.replace("\n", "") for l in f.readlines()]
            self.pf = ProfanityFilter(custom_censor_list=censor)

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

    def set_settings(self, host, port, chan, nick, auth, cooldown, access_token, allowed_ranks, allowed_users, custom_prompt):
        self.host, self.port, self.chan, self.nick, self.auth, self.cooldown, self.access_token, self.allowed_ranks, self.allowed_users, self.custom_prompt = host, port, chan, nick, auth, cooldown, access_token, [rank.lower() for rank in allowed_ranks], [user.lower() for user in allowed_users], custom_prompt

    def message_handler(self, m):
        if m.type == "366":
            logging.info(f"Successfully joined channel: #{m.channel}")
        elif m.type == "PRIVMSG":
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
            elif m.message.startswith("!help"):
                self.command_help(m)
            elif m.message.startswith("!restart") and self.check_permissions(m):
                self.command_restart(m)

    def extract_message(self, m):
        try:
            # Extract the message after the first space.
            return m.message[m.message.index(" ") + 1:]
        except ValueError:
            # If no spaces, return empty string
            return ""

    def check_permissions(self, m):
        for rank in self.allowed_ranks:
            if rank in m.tags["badges"]:
                return True
        return m.user.lower() in self.allowed_users

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
            out = f"Cooldown hit: {difference:.2f} out of {self.cooldown:.0f}s remaining. !nopm to stop these cooldown pm's."
            logging.debug(out)
            self.ws.send_whisper(m.user, out)
        return False

    def response_task(self, message, prefix, postfix, custom_output):
        # Get the actual output from the API
        out = self.api.say(prefix + message + postfix)

        # If a custom output is warranted for this action type, use that as output instead
        if custom_output:
            out = custom_output
        else:
            # Censor the output
            out = self.censor(out)
            
            # Convert to a better format, eg remove newlines.
            out = self.parse_output(out)

        if out:
            logging.info(f"Chat output: {out}")
            # If `out` could be considered a command, 
            # then prepend a space which does not get filtered out by twitch, 
            # which should prevent the message as being considered a command
            if out.startswith(("!", "~", ".", "/", "\\")):
                out = "⠀" + out
            self.ws.send_message(out)
        else:
            out = "AI Dungeon 2 responded with an empty message, sadly."
            logging.error(out)
            self.ws.send_message(out)

    def command_action(self, message, prefix="", postfix="", custom_output="", force=False):
        # If force is True, then we will communicate with the API even if the message is empty.

        # Function to handle communication between API and this class
        if message or force:

            logging.debug(f"Calling api.say with \"{prefix + message + postfix}\"")
            # Check if the input contains a banned word
            if self.is_clean(message):
                # Set the last_command_time to the current time for cooldown
                self.last_command_time = time.time()

                # Create a threading daemon task for sending responses to the API
                t = threading.Thread(target=self.response_task, args=(message, prefix, postfix, custom_output), daemon=True)
                t.start()
                return
            
            logging.warning(f"The input \"{message}\" was filtered out.")
            out = "This input contained a banned word or phrase!"
        else:
            out = "Please also enter a message alongside your command."
        
        logging.info(f"Chat output: {out}")
        self.ws.send_message(out)

    def is_clean(self, message):
        # True if message does not contain a banned word.
        return self.pf.is_clean(message)

    def censor(self, message):
        # Replace banned phrase with ***
        censored = self.pf.censor(message)
        if message != censored:
            logging.warning(f"Censored \"{message}\" into \"{censored}\".")
        return censored

    def command_do(self, m):
        if self.check_cooldown(m):
            # Force is True for `!do`, as an empty message will allow more dialoge to generate on its own
            self.command_action(self.extract_message(m), force=True)

    def command_remember(self, m):
        #if self.check_cooldown(m):
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

    def command_help(self, m):
        self.ws.send_message("!do <text> to take an action. !remember <text> to remember `text`. !revert to revert the last action. !event <text> to have `text` occur. !say <text> to speak `text`.")

    def parse_output(self, message):
        # TODO: Improve upon this. 
        # Make it so conversations with different perspectives are clearly separated.
        return message.replace("\n", " ")

    def restart_task(self):
        # Get a new session_id and story from a new adventure
        session_id, story = self.api.start(self.custom_prompt)
        # Only if successful
        if session_id:
            self.session_id = session_id
            self.ws.send_message(story)
            logging.debug("Successfully started new story.")
            logging.info(story)
        else:
            self.ws.send_message("Failed to restart story.")
            logging.error("Failed to start new story.")

    def command_restart(self, m):
        # Set the last_command_time to the current time for cooldown
        self.last_command_time = time.time()

        # Asyncronously start a new story
        t = threading.Thread(target=self.restart_task, daemon=True)
        t.start()

if __name__ == "__main__":
    TwitchAIDungeon()

"""
TODO: 
- Convert the output to a more readable format, when different perspectives are involved.
  - This has not proven to be much of an issue thus far
- Allow saving of all story data to a pastebin for chat.

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
