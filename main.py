
import discord
from discord.ext import commands
import token_reader as token
import scraper

from music import Music
from responder import Chat
 
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description='Julle-bot')
bot.add_cog(Music(bot))
bot.add_cog(Chat(bot))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
 
bot.run(token.get_token())