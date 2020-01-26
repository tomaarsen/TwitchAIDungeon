
from TwitchWebsocket import TwitchWebsocket

from Settings import Settings
from Log import Log
Log(__file__, Settings.get_channel())

class TwitchAIDungeon:
    def __init__(self):
        # Initialize variables to None
        self.host = None
        self.port = None
        self.chan = None
        self.nick = None
        self.auth = None
        capability = []
        self.cooldown = None
        
        # Update variables
        Settings(self)

        # Create Websocket object
        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=capability,
                                  live=True)
        # Start a blocking websocket connection
        self.ws.start_bot()

    def set_settings(self, host, port, chan, nick, auth, cooldown):
        self.host, self.port, self.chan, self.nick, self.auth, self.cooldown = host, port, chan, nick, auth, cooldown

    def message_handler(self, m):
        print(m)

if __name__ == "__main__":
    TwitchAIDungeon()
