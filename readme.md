# Install

## You need to run python 3
 - Use Pip to install the following pages
 - `pip install python-dotenv`
 - `pip install openai`
 - `pip install discord`

## download these project files from git
In a command prompt, be IN the folder you want to keep your files. Run the following command to clone these to your local machine

`git clone https://github.com/Wyseguys/discord-bot.git . `


## Local or Cloud
You can use this against a local LLM, or against OpenAI in the cloud

### If you are using a cloud based OpenAI
Log into your account, make a new API key and cut and paste it into the .env file, or maybe set it up in your environment. However. Its a secret so DON'T TELL ANYBODY YOUR KEY!!!

### If you want to run locally
 - Install LM Studio.
 - On the developer tab, click the "start server" button
 - Watch the server logs that stream past to make sure you are talking ot the local LLM

 ## Set up the environment
So you don't have to share secrets, copy the .env.example file in folder and rename the copy to .env.  Add your tokens to that file so the bot can read them. 

OPTIONALLY, you might also need to adjust your computer's command prompt PATH varaible.  Something along the lines of:

### For the linux crown (and maybe Apple? I don't know)

>`export DISCORD_TOKEN='your discord key'`

>`export OPENAI_TOKEN='your openai key'`

>`export PATH=$PATH:/bin/python` (or wherever your python is installed)

### Windows Geeks can use Powershell
> `$env:DISCORD_TOKEN = 'discord key here'`

> `$env:OPENAI_TOKEN = 'discord key here'`

> `$env:PATH = ';/bin/pythong'`  (but again, I don't know I didn't test this on windows)


### Or boring old command prompt
Look it up yourself. Or use powershell because it's cooler



## Run it.
Still in the same folder as the bot.py file, run it in python

`python3 bot.py`