import time

from fastapi import FastAPI, Request , Response
from fastapi.responses import PlainTextResponse
import requests


import config
from config import  VERIFICATION_TOKEN
from senderActions import mark_message_seen, show_typing
import ollama
from ollama import chat
from mongodb import system_prompt,tools,available_functions ,model_name
app = FastAPI()
from fastapi import BackgroundTasks


model="qwen2.5:14b"

user_dic= {}

@app.get("/webhook")
async def verify(request: Request):
    """
    Endpoint to verify Facebook webhook setup.
    """
    mode = request.query_params.get('hub.mode')
    token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFICATION_TOKEN:
        return PlainTextResponse(challenge)
    else:
        return PlainTextResponse("Verification failed", status_code=403)

def send_message(recipient_id: str, message: dict) -> dict:
    """
    Send a message using Facebook's Send API.
    """
    url = f"https://graph.facebook.com/v11.0/me/messages?access_token={config.BOT_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": message
    }
    response = requests.post(url, json=payload, headers=headers)

    return response.json()




def get_ai_response(id , message):
    if id not in user_dic:
        user_dic[id]= [  {'role': 'system', 'content': system_prompt},
            {'role': 'assistant', 'content': 'OK I understand. I will do my best!'}]
    user_dic[id].append({"role" : "user" , "content": message})
    if len(user_dic[id])>70:
        user_dic[id]=[  {'role': 'system', 'content': system_prompt},
            {'role': 'assistant', 'content': 'OK I understand. I will do my best!'}]+user_dic[id][-70:]

    response =  chat(
    model_name,
    messages=user_dic[id],
    tools=tools
    )
    user_dic[id].append(response.message)

    if response.message.tool_calls:
        used_tools=[]
        while response.message.tool_calls:
            # print("function called")
            print(response.message.tool_calls)
            for tool in response.message.tool_calls:
                if tool.function.name in used_tools:
                    continue
                used_tools.append(tool.function.name)
                print("tool name : " + tool.function.name)
                if tool.function.name in available_functions:
                    funct = available_functions[tool.function.name]
                    result = str(funct(**tool.function.arguments)) + "\n"
                else:
                    continue
                # print(result)
                # Add the function response to messages for the model to use
                user_dic[id].append({'role': 'tool', 'content': str(result), 'name': tool.function.name})
            response = chat(model_name, messages=user_dic[id], tools=tools)
            user_dic[id].append(response.message)
        return {"text": response.message.content}

    else :
        return {"text": response.message.content}


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming webhook events from Facebook.
    Returns a 200 OK with 'EVENT_RECEIVED' as required by Facebook.
    """
    data = await request.json()
    print("Received a message event")
    start = time.time()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                background_tasks.add_task(process_message, event)
        # Return the exact response as specified in the docs
        end =time.time()
        return PlainTextResponse("EVENT_RECEIVED", status_code=200)
    else:
        return Response(status_code=404)

import asyncio

async def process_message(event):
    try:
        sender_id = event['sender']['id']
        mark_message_seen(sender_id)
        show_typing(sender_id, True)

        if 'message' in event:
            textmessage = event["message"].get("text")

            if textmessage:
                print("Processing message:", textmessage)
                # Offload the blocking AI call to a thread
                botresponse = await asyncio.to_thread(get_ai_response, sender_id, textmessage)
                print("Sending message:", botresponse)
                # Offload sending the message as well if it uses blocking calls
                await asyncio.to_thread(send_message, sender_id, botresponse)

        show_typing(sender_id, False)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":



    #if __name__ == "__main__":
    import uvicorn
    import os
    import sys

    # Determine if we are running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))

    ssl_key_path = os.path.join(base_path, "sslVerification", "fernabot.top.key")
    ssl_cert_path = os.path.join(base_path, "sslVerification", "fullchain.pem")

    uvicorn.run(
        app,
        port=8000,

    )
    """
    uvicorn.run(
        app,
    host = "0.0.0.0",

    ssl_keyfile = ssl_key_path,
    ssl_certfile = ssl_cert_path

    )"""



