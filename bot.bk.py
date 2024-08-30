import requests
from dotenv import load_dotenv
import discord
from openai import OpenAI
import os
import asyncio
import aiohttp


load_dotenv()
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

#Create an instance of a client with appropriate intents
intents=discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
discord_client = discord.Client(intents=intents)


async def make_post_request(session, url, headers, data):
    try:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                print("Request successful. Response:", await response.json())
                choices = await response.json()["choices"]
                for choice in choices:
                    message_content = choice["message"]["content"]
                    print(f"Message Content: {message_content}")
                    return message_content
    
    except aiohttp.ClientResponseError as e:
        print(f"Error making request: {e}")

async def get_llm_response_local(url, headers, data):
    async with aiohttp.ClientSession() as session:
        response_data = await make_post_request(session, url, headers, data)
        if response_data is not None:
            print("Request successful. Response:", response_data)
            return response_data

@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')

@discord_client.event
async def on_message(message):
    print(message)
    
    # Don't let the bot reply to itself
    if message.author == discord_client.user:
        print("\nDon't talk to yourself bot.")
        return

    #TODO: make sure this bot doesn't start talking to other bots

    try:
        message.channel.name
    except AttributeError:
        print("\nwell, the message isn't in a channel, it is a DM!")
        #I know what the message is, I can deal with it
        message_content = message.content
    else:
        print("\nChannel ID: %s" % message.channel.id)
        #I will get the last message from the channel
        last_message = discord_client.get_channel(message.channel.id).last_message
        message_content = last_message.content


    #TODO: we can check if its the right channel, and only respond there

    print("\nContent: %s" % message_content)

    # Check if the message starts with a specific prefix for DM commands
    if message_content.startswith('!dmz'):
        
        player_action = message_content[len('!dmz'):].strip()
        
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


        url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "messages": [
            { "role": "system", "content": "You are a Dungeon Master guiding players through a fantasy adventure. Respond with rich descriptions and actions based on the player's inputs." },
                    {
                        "role": "user",
                        "content": message_content
                    }
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        try:
            #dm_response = make_post_request(url, headers, data)
            await message.channel.send(await get_llm_response_local(url, headers, data))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")


                
        #await message.channel.send(dm_response)
        
#Run the bot with the token
discord_client.run(DISCORD_TOKEN)