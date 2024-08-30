import requests
from dotenv import load_dotenv
import discord
from openai import OpenAI
import os
import asyncio
import aiohttp
from gamemaster import GameMaster




# class LlmClient:
#     def __init__(self):
#         self.session = None

#     async def init_session(self):
#         if not self.session:
#             self.session = aiohttp.ClientSession()

#     async def make_request(self, url, headers, data):
#         await self.init_session()
#         async with self.session.post(url, json=data, headers=headers) as response:
#             # Process the response







# llm_client = LlmClient()
# await llm_client.init_session()


Is_First_Message = True
DEBUG_MESSAGES = True

load_dotenv()
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


async def make_post_request(session, url, headers, data):
    try:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                choices = await response.json()
                message_content = choices["choices"][0]["message"]["content"]
                return message_content
    
    except aiohttp.ClientResponseError as e:
        print(f"Error making request: {e}")
        return None

async def get_llm_response_local(player_action):
    global Is_First_Message
    gm = GameMaster("DM")

    async with aiohttp.ClientSession() as session:

        if DEBUG_MESSAGES: print(f"Is this the 1st Message: {Is_First_Message}")
        if Is_First_Message: Is_First_Message = False


        if Is_First_Message:
            system_role_content = gm.load_main_system_role()
        else:
            system_role_content = gm.load_reminder_system_role()


        url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "messages": [                
                { "role": "system", "content": system_role_content },
                { "role": "user", "content": player_action }
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        response_data = await make_post_request(session, url, headers, data)
        if response_data is not None:
            if DEBUG_MESSAGES: print("Request successful. Response:", response_data)
            return response_data

#async def get_llm_response_openai(player_action):
            #TODO: I be we can give more "role" context to chatgpt and it can remember the campaign?
        # try:
        #     client = OpenAI(api_key=OPENAI_TOKEN)
        #     completion = client.chat.completions.create(
        #         model="gpt-4o-mini",
        #         messages=[
        #             {"role": "system", "content": "You are a Dungeon Master guiding players through a fantasy adventure. Respond with rich descriptions and actions based on the player's inputs."},
        #             {
        #                 "role": "user",
        #                 "content": message.sender.name + " says " + player_action
        #             }
        #         ]
        #     )
        # except Exception as e:
        #     await message.channel.send(f"An error occurred: {str(e)}")

        # dm_response = completion.choices[0].message.content
        # print(dm_response)


async def chat_with_llm(message, player_action):
    try:
        #dm_response = make_post_request(url, headers, data)
        await message.channel.send(await get_llm_response_local(player_action))

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

    gm = GameMaster("DM")
    player_action = gm.prepare_message(message, message_content)

    await chat_with_llm(message, player_action)
    
#Run the bot with the token
discord_client.run(DISCORD_TOKEN)