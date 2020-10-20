import os
from dotenv import load_dotenv
import json
import requests
import discord
from discord.ext import commands
from igdb.wrapper import IGDBWrapper

load_dotenv()

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def search(ctx, arg):
    # Establish authentication through Twitch
    twitch = requests.post(f'https://id.twitch.tv/oauth2/token?client_id={os.environ.get("TWITCH_ID")}&client_secret={os.environ.get("TWITCH_SECRET")}&grant_type=client_credentials')
    oAuth = twitch.json()
    # Create a new IGDBWrapper object with Twitch access token.
    wrapper = IGDBWrapper(os.environ.get("TWITCH_ID"), oAuth['access_token'])
    # JSON API request
    byte_array = wrapper.api_request(
                'games',
                f'fields name,first_release_date,platforms.name,cover.url,summary;search "{arg}";limit 1;'
                )

    # Parse JSON
    game_info = json.loads(byte_array)

    # Loop through platforms and extract platform name
    platforms = []
    for n in game_info[0]['platforms']:
        name = n['name']
        platforms.append(name)

    # Parse and format release date
    

    # Set up embeded message
    embed = discord.Embed(title=game_info[0]['name'], color=0x1f436e)
    embed.set_image(url=f"https:{game_info[0]['cover']['url']}")
    embed.add_field(name='Platforms', value=f"{' / '.join(platforms)}")
    embed.add_field(name='Release Date', value=f"{}")
    
    print(game_info[0])
    await ctx.channel.send(embed=embed)

client.run(os.environ.get('DISCORD_TOKEN'))