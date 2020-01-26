
import requests, json, os

# Run this to continue your most recently made adventure

# Use your OS' environment variable to get the access token
headers = {"X-Access-Token": os.environ["AI_DUNGEON_ACCESS_TOKEN"]}

response = requests.get("https://api.aidungeon.io/sessions", headers=headers)
content = json.loads(response.text)
session_id, story = max((adventure["id"], adventure["story"]) for adventure in content)

# Print previous story
for message in story:
    if message["type"] == "input":
        print(">", end="")
    print(message["value"])
    print()

while True:
    # Get json data sent alongside POST request
    json_data = {"text": input(">")}

    response = requests.post(f"https://api.aidungeon.io/sessions/{session_id}/inputs", json=json_data, headers=headers)
    content = json.loads(response.text)
    print(content[-1]["value"])
