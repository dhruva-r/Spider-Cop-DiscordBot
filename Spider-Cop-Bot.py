# This example requires the 'message_content' intent.

import discord
from googleapiclient import discovery
import json
import config

# defined in a file called config.py (not pushed to github because that would not be wise :D)
API_KEY = config.API_KEY
DISCORD_TOKEN = config.DISCORD_TOKEN


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
    
    # There should be other conditions to prevent running the api call over and over
    
    score = toxicity_analysis(message.content)
    print(score)

    if score > 0.90:
        await message.channel.send('Shutup you toxic fucking bitch')

def toxicity_analysis(message: str):
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

