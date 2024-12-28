# This example requires the 'message_content' intent.

import discord
from googleapiclient import discovery
import json
import config
import random

# defined in a file called config.py (not pushed to github because that would not be wise :D)
API_KEY = config.API_KEY
DISCORD_TOKEN = config.DISCORD_TOKEN
answers = config.responses 


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # We don't want the bot to analyze itself
    if message.author == client.user:
        return
    
    # prevents analysis on attachments
    if message.attachments:
        return
    
    # prevents analysis on links 
    if 'https://' in message.content:
        return
        
    score = toxicity_analysis(message.content)
    print(score)

    # This value in this conditional is arbitrary 
    if score > 0.90:
        # the array answers, is defined in config.py and contains cdn's of images and responses
        # the random library picks any of these messages at random to send to the user
        await message.reply(random.choice(answers))

    # TODO adding a tier list of some sort (tracks the most toxic messages :) )

def toxicity_analysis(message: str) -> int:
    clienttwo = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=API_KEY,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
    )

    analyze_request = {
    'comment': { 'text': message },
    'requestedAttributes': {'TOXICITY': {}}
    }
    response = clienttwo.comments().analyze(body=analyze_request).execute()
    response = json.dumps(response, indent=2)
    response = json.loads(response)
    return response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
    

client.run(DISCORD_TOKEN)

