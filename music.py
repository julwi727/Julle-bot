
import asyncio
import discord
from discord.ext import commands

from voicestate import VoiceState
from voiceentry import VoiceEntry

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
 
    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state
 
        return state
 
    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice
 
    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass
 
    
    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Inkallar mig till din kanal."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('Du är inte i en kanal.')
            return False
 
        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)
 
        return True

    """
    @commands.command(pass_context=True, no_pm=True)
    async def search(self, ctx):
        search = "+".join(ctx.message.content.split(" ")[1:])
        print(str(ctx.message.author) + ' searched for ' + search)

        results_tuple = scraper.scrape_yt(search)

        author = ctx.message.channel

        embed = discord.Embed(
            colour = discord.Colour.red()
        )

        embed.set_author(name = 'Sökresultat')
        embed.add_field(name = "1. " + results_tuple[1][0], value = results_tuple[0][0] + " (" + results_tuple[2][0] + ")", inline = True)
        embed.add_field(name = "2. " + results_tuple[1][1], value = results_tuple[0][1] + " (" + results_tuple[2][1] + ")", inline = True)
        embed.add_field(name = "3. " + results_tuple[1][2], value = results_tuple[0][2] + " (" + results_tuple[2][2] + ")", inline = True)
        embed.add_field(name = "4. " + results_tuple[1][3], value = results_tuple[0][3] + " (" + results_tuple[2][3] + ")", inline = True)
        embed.add_field(name = "5. " + results_tuple[1][4], value = results_tuple[0][4] + " (" + results_tuple[2][4] + ")", inline = True)
        
        await self.bot.send_message(author, embed=embed)
    """
    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Spelar upp eller söker på låt (YouTube)"""
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }
 
        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return
 
        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'Fel uppstod: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            if "https://www.youtube" in player.url:
                state.current_youtube_url = player.url
            else:
                state.current_youtube_url = "https://youtube.com/watch?v={}".format(player.yt.extract_info(player.url, download=False)["entries"][0]["id"])
            await state.songs.put(entry)
 
    
    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pausar låt"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
 
    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Återupptar uppspelning av låt"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
 
    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stoppar uppspelning av låt och kastar ut mig ur kanalen"""
        server = ctx.message.server
        state = self.get_voice_state(server)
 
        if state.is_playing():
            player = state.player
            player.stop()
 
        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass
 
    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Byter till nästa låt i kön"""
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Ingen låt spelas.')
            return
        
        state.skip()

        if state.songs.empty():
            await self.bot.say('Kön är nu tom.')
       
       
 
    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Information om låt som spelas just nu"""
 
        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Ingenting spelas.')
        else:
            await self.bot.say("Nu spelas " + str("https://youtube.com/watch?v={}".format(state.player.yt.extract_info(state.player.url, download=False)["entries"][0]["id"])))
 