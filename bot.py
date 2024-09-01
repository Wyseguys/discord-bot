import requests
from dotenv import load_dotenv
import discord
from openai import OpenAI
import os
import asyncio
import aiohttp
from gamemaster import GameMaster


DEBUG_MESSAGES = True           #(True or False) - barf out a bunch of debugging messages in the python terminal

GAMEMASTER_NAME = "GM"          #Maybe give the GM a name? I don't use it now, but perhaps we can

# When we say "Local LLM" I test it using LM Studio. I downloaded the small LLAMA3.1 model.  The URL is the default
# URL when you use LM Studio to serve, and the Model is the API identifier
LOCAL_LLM_ENABLED   = True      #(True or False) - We prefer a local LLM because it's free
LOCAL_LLM_URL       = "http://localhost:1234/v1/chat/completions"
LOCAL_LLM_MODEL     = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
LOCAL_LLM_TEMP      = 0.7       #(0 > 1) - How creative the model is supposed to be

OPEN_AI_ENABLED = False         #(False or True) - If you use OpenAI, turn off the local and turn this True
OPEN_AI_MODEL = "gpt-4o-mini"   # How many pennies do you have?

#LOCAL SECRETS. We're storing these as environment variables. Don't put secrets in the public 
# respository.
load_dotenv()
OPENAI_TOKEN  = os.getenv('OPENAI_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

########################################
#GLOBAL VARIABLES, DON'T MESS WITH THESE
########################################
Is_First_Message = True

def get_gm_instructions(is_first_message):
    """
    Either load the long instructions because it is the first message of the session, or load
    the reminder text that should keep the game master on track
    """
    global Is_First_Message
    if DEBUG_MESSAGES: print(f"Is this the 1st Message: {Is_First_Message}")
    
    gm = GameMaster(GAMEMASTER_NAME)
    
    if is_first_message:
        system_role_content = gm.load_main_system_role()
        Is_First_Message = False
    else:
        system_role_content = gm.load_reminder_system_role()

    return system_role_content


async def get_llm_response_local(player_action):
    """
    Format a request and response to a locally running LLM.
    """
    global Is_First_Message

    async with aiohttp.ClientSession() as session:

        if DEBUG_MESSAGES: print(f"Is this the 1st Message: {Is_First_Message}")
        system_role_content = get_gm_instructions(Is_First_Message)
        if Is_First_Message: Is_First_Message = False

        url = LOCAL_LLM_URL
        headers = {"Content-Type": "application/json"}
        data = {
            "model": LOCAL_LLM_MODEL,
            "messages": [                
                { "role": "system", "content": system_role_content },
                { "role": "user", "content": player_action }
            ],
            "temperature": LOCAL_LLM_TEMP,
            "max_tokens": -1,
            "stream": False
        }

        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    choices = await response.json()
                    response_data = choices["choices"][0]["message"]["content"]        
        except aiohttp.ClientResponseError as e:
            print(f"Error making request: {e}")
            return None

        if response_data is not None:
            if DEBUG_MESSAGES: print("Request successful. Response:", response_data)
            return response_data

async def get_llm_response_openai(player_action):
    """
    Using the OpenAI python package, send the request and response to chatgpt model
    """
    global Is_First_Message
    system_role_content = get_gm_instructions(Is_First_Message)

    try:
        client = OpenAI(api_key=OPENAI_TOKEN)
        completion = client.chat.completions.create(
            model=OPEN_AI_MODEL,
            messages=[
                { "role": "system", "content": system_role_content },
                { "role": "user", "content": player_action }
            ]
        )

        dm_response = completion.choices[0].message.content
        if DEBUG_MESSAGES: print(dm_response)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    if dm_response is not None:
        if DEBUG_MESSAGES: print("Request successful. Response:", dm_response)
        return dm_response


async def chat_with_llm(message, player_action):
    """
    Discord doesn't need to know LLM it is talking to, so figure it out here
    based on the configuration at the top of the script
    """
    try:
        if LOCAL_LLM_ENABLED:
            await message.channel.send(await get_llm_response_local(player_action))
        
        if OPEN_AI_ENABLED:
            await message.channel.send(await get_llm_response_openai(player_action))

    except Exception as e:
        print(f"An unexpected error occurred: {e}")




#Create an instance of a client with appropriate intents
intents=discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')

@discord_client.event
async def on_message(message):
    """
    Wait for the discord message to arrive. Don't let the bot talk to itself. Also, if the message comes from a channel
    we'll have to guess the last message in that channel is the one to act on.

    Finally, send the message to the LLM
    """
    if DEBUG_MESSAGES: print(message)
    
    # Don't let the bot reply to itself
    if message.author == discord_client.user:
        print("\nDon't talk to yourself bot.")
        return

    try:
        message.channel.name
    except AttributeError:
        print("\nwell, the message isn't in a channel, it is a DM!")
        message_content = message.content  #I know what the message is, I can deal with it
    else:
        print("\nChannel ID: %s" % message.channel.id)
        last_message = discord_client.get_channel(message.channel.id).last_message #I will get the last message from the channel
        message_content = last_message.content

    if DEBUG_MESSAGES: print("\nContent: %s" % message_content)

    gm = GameMaster(GAMEMASTER_NAME)
    player_action = gm.prepare_message(message, message_content)

    await chat_with_llm(message, player_action)
    
#Run the bot with the token
discord_client.run(DISCORD_TOKEN)