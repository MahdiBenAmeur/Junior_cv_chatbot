BOT_TOKEN="EAAHGHT8rQEABOxZA5qUWT01fxUuzY5VNZAGlKSKiAPfAFSJLTbHNU7GZAP7WbWS5fKekL3NdMz534hlJALrIe3hKvfxg94cOZBV3cA7vztJkwtahfjqZCglRGwhy4SoPbJUX1qjkTdeuZACXU04mf8Sgr56AUXUTkzJX2q6Bjoe6A1uWa8axUCnERDTsZCsZBb8CJgZDZD"
VERIFICATION_TOKEN="fernabottopsercittokenHFGFkjuiohi454854"
PAGE_ID="518692844668143"
FB_API_URL='https://graph.facebook.com/v12.0/me/messages'

import os
import sys
import json

if getattr(sys, 'frozen', False):
    # The executable is running in a frozen state
    # sys.executable is the full path to the main.exe file
    base_path = os.path.dirname(sys.executable)
else:
    # Running in normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_path, "config.json")

with open(config_path, "r") as f:
    configurations = dict(json.load(f))
BOT_TOKEN = configurations["pageconfig"]["BOT_TOKEN"]
PAGE_ID = configurations["pageconfig"]["PAGE_ID"]

#t_1567769057468221/messages?limit=20&fields=message,from,to,created_time

#https://a879-102-157-49-247.ngrok-free.app/webhook?hub.mode=subscribe&hub.challenge=773490065&hub.verify_token=fernabottopsercittokenHFGFkjuiohi454854