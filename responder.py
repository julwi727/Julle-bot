import discord
from discord.ext import commands

hi = ['yo', 'suh dude', 'tjenamors', 'morsning korsning', 'tjenare italienare', 'Hur står det till?', 'Vad görs bre', 'Fan tja det var inte igår', 'Hej']
games = ['Overwatch', 'Guild Wars 2', 'Borderlands', 'Jackbox', 'Runescape', 'Tibia', 'CS:GO', 'Keep talking and Nobody Explodes', 'GTA V', 'Rocket League', 'Golf it!', 'Quake', 'Unreal Tournament', 'Warframe', 'CS Source', 'Heroes III', 'AoE II', 'Worms', 'Terraria', 'Starbound', 'Rollercoaster Tycoon 2', 'Riven', 'The Sims 3', 'Din mamma såklart']

import datetime
import random
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot('Julle')

chatbot.set_trainer(ChatterBotCorpusTrainer)
chatbot.trainer.train("chatterbot.corpus.swedish")

def get_hi():
    return random.choice(hi)

def get_game():
    return random.choice(games)

def process_message(msg):
    if '?' in msg:
        if 'vilket' in msg and 'spel' in msg:
            return get_game()

        elif 'vad' in msg and 'spel' in msg:
            return get_game()

        elif 'klockan' in msg: 
            now = datetime.datetime.now()
            response = 'Klockan är ' + now.strftime("%H:%M")  
            return response

        elif 'datum' in msg or 'dag' in msg:
            now = datetime.datetime.now()
            response = "Dagens datum är " + now.strftime("%Y-%m-%d")  
            return response

        elif 'vecka' in msg:
            now = datetime.datetime.now()
            response = 'Just nu är det vecka ' + str(1 + int(now.strftime("%U")))  
            return response

    return chatbot.get_response(msg)


class Chat:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def say(self, ctx):
        """Säg något eller ställ en fråga till mig"""
        await self.bot.say(process_message(ctx.message.content[5:]))

    @commands.command(pass_context = True)
    async def tjena(self, ctx):
        """Hälsa på mig"""
        await self.bot.say(get_hi())