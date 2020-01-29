
import logging, requests, json
# Disable info logs from urllib3 used by requests
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class API:
    def __init__(self, taid):
        super().__init__()
        self.taid = taid

    def say(self, message):
        logger.debug(f"Sending \"{message}\" to the AI Dungeon 2 API...")
        # Get the headers using the access token
        headers = {"X-Access-Token": self.taid.access_token}
        # Get json data sent alongside POST request
        json_data = {"text": message}
        # Get the response with this message, session_id and headers
        response = requests.post(f"https://api.aidungeon.io/sessions/{self.taid.session_id}/inputs", json=json_data, headers=headers)
        if response.status_code == 200:
            content = json.loads(response.text)
            out = content[-1]["value"]
            logger.debug(f"Received \"{out}\" from the AI Dungeon 2 API.")
            # Return the message itself
            return out
        else:
            logger.error(f"Response code was {response.status_code}.")
            return ""

    def get_session_id(self):
        logger.debug("Fetching session_id from AI Dungeon 2 API...")
        # Get the headers using the access token
        headers = {"X-Access-Token": self.taid.access_token}
        # Get the response of all open sessions
        response = requests.get("https://api.aidungeon.io/sessions", headers=headers)
        if response.status_code == 200:
            content = json.loads(response.text)
            # Get the newest made session
            session_id, story = max((adventure["id"], adventure["story"]) for adventure in content)
            # Story is discarded for now. It's all input and output so far.
            logger.debug(f"Finished fetching session_id ({session_id}) from AI Dungeon 2 API.")
            return session_id
        else:
            logger.error(f"Response code was {response.status_code}.")
            return ""

    def start(self):
        logger.debug("Starting a new custom adventure...")
        # Get the headers using the access token
        headers = {"X-Access-Token": self.taid.access_token}
        json_data = {
            "storyMode": "custom",
            "characterType": None,
            "name": None,
            "customPrompt": "We are Malfius Yabeb in the NLSS Universe. We live in Skokie Illinois, and our task is to find the ultimate Team Unity Tuesday game. We start out in Vancouver hanging out with Ryan Gary.",
            "promptId": None
        }
        response = requests.post("https://api.aidungeon.io/sessions", json=json_data, headers=headers)
        if response.status_code == 200:
            content = json.loads(response.text)
            logger.debug("Started a new custom adventure.")
            return content["id"], content["story"][0]["value"]
        else:
            logger.error(f"Response code was {response.status_code}.")
            return None, None