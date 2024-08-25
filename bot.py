from dotenv import load_dotenv
import discord
from openai import OpenAI
import os


load_dotenv()
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

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
    if message_content.startswith('!dm'):
        
        player_action = message_content[len('!dm'):].strip()
        
        #TODO: I be we can give more "role" context to chatgpt and it can remember the campaign?
        try:
            client = OpenAI(api_key=OPENAI_TOKEN)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Dungeon Master guiding players through a fantasy adventure. Respond with rich descriptions and actions based on the player's inputs."},
                    {
                        "role": "user",
                        "content": player_action
                    }
                ]
            )
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

        dm_response = completion.choices[0].message.content
        print(dm_response)
                
        await message.channel.send(dm_response)
        
#Run the bot with the token
discord_client.run(DISCORD_TOKEN)