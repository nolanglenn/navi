import os
from dotenv import load_dotenv
import json
import requests
import discord
import datetime
import emoji
import sheets
from sheets import searched_titles
from sheets import episode
from discord.ext import commands
from igdb.wrapper import IGDBWrapper

load_dotenv()

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def search(ctx, *, arg=None):
    # Input validation
    if arg == None:
        return await ctx.channel.send('Please provide a game.')
    # Establish authentication through Twitch
    twitch = requests.post(f'https://id.twitch.tv/oauth2/token?client_id={os.environ.get("TWITCH_ID")}&client_secret={os.environ.get("TWITCH_SECRET")}&grant_type=client_credentials')
    oAuth = twitch.json()
    # Create a new IGDBWrapper object with Twitch access token.
    wrapper = IGDBWrapper(os.environ.get("TWITCH_ID"), oAuth['access_token'])
    # JSON API request
    byte_array = wrapper.api_request(
                'games',
                f'fields name,first_release_date,platforms.name,cover.url;search "{arg}";limit 5;'
                )

    # Parse JSON
    game_info = json.loads(byte_array)

    # Loop through platforms and extract platform name
    platforms = []
    try:
        for n in game_info[0]['platforms']:
            name = n['name']
            platforms.append(name)
    except Exception:
        pass

    # Parse and format release date and determine if game is eligible (15 years old or oler)

    release_date = datetime.datetime.fromtimestamp(
                        int(game_info[0]['first_release_date'])
                    ).strftime("%B %d, %Y")
    
    def eligible():
        if datetime.datetime.fromtimestamp(int(game_info[0]['first_release_date'])) <= datetime.datetime.now() - datetime.timedelta(days=15*365):
            return emoji.emojize(':white_check_mark:')
        else:
            return emoji.emojize(':no_entry_sign:')

    # Fetch thumbnail if it exists
    def thumbnail():
        cover = discord.Embed.Empty
        try:
            if game_info[0]['cover']:
                cover = f"https:{game_info[0]['cover']['url']}"
                return cover
            else:
                return discord.Embed.Empty
        except Exception:
            return cover
        else:
            return cover
    
    # Search Retro Master List with Google Sheets API
    def on_list():
        try:
            sheets.main()
            if game_info[0]['name'] in searched_titles:
                return 'Yes'
            else:
                embed.set_footer(name ='Note:', value='You will be able to add this game by reating in future iterations of this bot.')
                return 'No'
        except Exception:
            pass
      
    # Set up embeded message
    embed = discord.Embed(title=game_info[0]['name'], color=0x1f436e)
    embed.set_thumbnail(url=thumbnail())
    embed.add_field(name='Platform(s)', value=' / '.join(platforms))
    embed.add_field(name='Release Date', value=release_date, inline=False)
    embed.add_field(name='Eligible?', value=eligible())
    embed.add_field(name='On list?', value=on_list(), inline=True)
    
    print(game_info[0])
    await ctx.channel.send(embed=embed)

client.run(os.environ.get('DISCORD_TOKEN'))