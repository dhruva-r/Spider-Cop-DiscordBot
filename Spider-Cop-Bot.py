# This example requires the 'message_content' intent.

import discord
from googleapiclient import discovery
import json
import config
import random
from discord.ext import commands

# defined in a file called config.py (not pushed to github because that would not be wise :D)
API_KEY = config.API_KEY
DISCORD_TOKEN = config.DISCORD_TOKEN
answers = config.responses 


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

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
    
    # runs the api if the leaderboard command is not in the message (could use starts with as well)
    if '!leaderboard' not in message.content:
        score = toxicity_analysis(message.content)
        print(score)

        # This value in this conditional is arbitrary 
        if score > 0.88:
            # the array answers, is defined in config.py and contains cdn's of images and responses
            # the random library picks any of these messages at random to send to the user
            await message.reply(random.choice(answers))
            update_toxicity_count(message.guild.id, message.author.name)

    await client.process_commands(message)  # Allow commands to be processed

# Connects to the perspective API to peform a check on if the message is toxic
# Uses an NLP to accomplish this
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
    # We grab the probability
    return response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]


# Whenever the perspective call deems a message toxic, the count is then updated
# JSON file because scalability is not required and this is relatively simple to use
def update_toxicity_count(guild_id, user_id):
    """Update the count of toxic messages for a user in a JSON file."""
    try:
        with open('count.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Initialize guild and user data if not present
    if str(guild_id) not in data:
        data[str(guild_id)] = {}
    if user_id not in data[str(guild_id)]:
        data[str(guild_id)][user_id] = {"count": 0}

    # Increment the toxic message count
    data[str(guild_id)][str(user_id)]["count"] += 1

    # Save the updated data back to the JSON file
    with open('count.json', 'w') as f:
        json.dump(data, f, indent=4)


# Leaderboard command called with !leaderboard
@client.command()
async def leaderboard(ctx, x=10):
    with open('count.json', 'r') as f:
        users = json.load(f)

    guild_id = str(ctx.guild.id)

    if guild_id not in users:
        await ctx.send("No data available for this server.")
        return

    leaderboard = []

    for user, data in users[guild_id].items():
        leaderboard.append((user, data['count']))

    # Sort the leaderboard by count in descending order
    leaderboard.sort(key=lambda item: item[1], reverse=True)

    em = discord.Embed(
        title=f'Top {x} most toxic members of {ctx.guild.name}',
        description='hall of shame..'
    )

    for index, (user, count) in enumerate(leaderboard[:x], start=1):
        # Might add a tier break system as well using the value section
        em.add_field(name=f'**#{index}**: **{user}**', value="", inline=False)

    await ctx.send(embed=em)

if __name__=="__main__":
    client.run(DISCORD_TOKEN)

