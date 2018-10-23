import discord
import youtube_dl

import responder
import token_reader as token
import scraper

from discord.ext import commands

TOKEN = token.get_token()

client = commands.Bot(command_prefix = '!')
client.remove_command('help')

in_voice = False

players = {}
queues = {}
searches = {}

def check_queue(id):
    print('check_queue(id)')
    if queues[id] != []:
        print('currently %d songs in the queue ' % len(queues[id]))
        queue_list = queues[id]
        print('stopping song: ' + queue_list[0].url)
        queue_list[0].stop()
        queue_list.pop(0)
        print('currently %d songs in the queue ' % len(queues[id]))
        if len(queue_list) > 0:
            player = queue_list[0]
            players[id] = player
            player.start()
            client.say('Nu spelas: ' + player.url)
        else:
            client.say('Inga låtar i kön.')
    

@client.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    global in_voice
    in_voice = True
    await client.join_voice_channel(channel)

@client.command(pass_context = True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    global in_voice
    in_voice = False
    await voice_client.disconnect()

@client.command()
async def tjena():
    await client.say(responder.get_hi())

@client.command(pass_context = True)
async def help(ctx):
    author = ctx.message.channel

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name = 'Help')
    embed.add_field(name = '!tjena', value = 'Hälsa på Julle', inline = False)
    embed.add_field(name = '!say', value = 'Säg någonting till Julle\nTips: ställ en fråga med ett avslutande \'?\'', inline = False)
    embed.add_field(name = '!play [youtube url]', value = 'Spela upp ljud från youtube', inline = False)
    embed.add_field(name = '!clear', value = 'Rensa låtkön', inline = False)
    embed.add_field(name = '!pause', value = 'Pausa låt', inline = False)
    embed.add_field(name = '!resume', value = 'Återuppta uppspelning av låt', inline = False)
    embed.add_field(name = '!skip', value = 'Spela nästa låt i kön', inline = False)
    
    await client.send_message(author, embed=embed)

@client.command(pass_context = True)
async def say(ctx):
    msg = '{0.author.mention} '.format(ctx.message)
    msg += responder.process_message(ctx.message.content)
    await client.say(msg)

@client.event
async def on_ready():
    print('Bot is ready')

@client.command(pass_context = True)
async def play(ctx, url):
    print(str(ctx.message.author) + ' wants to play song ' + url)
    global in_voice
    if not in_voice:
        channel = ctx.message.author.voice.voice_channel
        await client.join_voice_channel(channel)
        in_voice = True
    
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    song_url = url
    search_choice = -1

    if len(url) == 1 and server.id in searches: #This is a search result
        try:
            search_choice = int(url)
        except ValueError:
            await client.say("Låtnummer måste vara en siffra.")
            return

        if 1 <= search_choice <= 5:
            song_url = searches[server.id][search_choice - 1]
            searches[server.id] = [] #successfully found a yt-url, reset search results
        else:
            await client.say("Låtnummer måste vara mellan 1-5.")

    player = await voice_client.create_ytdl_player(song_url, after=lambda: check_queue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    
    print('currently %d songs in the queue ' % len(queues[server.id]))
    if len(queues[server.id]) == 1:
        players[server.id] = player

        player.start()
        await client.say('Spelar låt ' + song_url)
    else:
        await client.say(song_url + ' tillagd i kön.\nJust nu är det %d låtar i kön.' % len(queues[server.id]))

@client.command(pass_context = True)
async def clear(ctx):
    print(str(ctx.message.author) + ' cleared queue')
    server = ctx.message.server
    for player in queues[server.id]:
        player.stop()

    if(len(queues[server.id]) > 0):
        queues[server.id].clear()
        players[server.id] = None
        await client.say('Just nu är det %d låtar i kön.' % len(queues[server.id]))
    else:
        await client.say('Kön är tom.')

@client.command(pass_context = True)
async def skip(ctx):
    print(str(ctx.message.author) + ' skipped song')
    server = ctx.message.server
    print('currently %d songs in the queue ' % len(queues[server.id]))
    players[server.id].stop()
    print('currently %d songs in the queue ' % len(queues[server.id]))
    
    if(len(queues[server.id]) > 0): 
        await client.say('Byter till nästa låt.')
        await client.say('Nu spelas: ' + players[server.id].url)
    else:
        await client.say('Kön är tom.')
    

@client.command(pass_context = True)
async def pause(ctx):    
    print(str(ctx.message.author) + ' paused song')
    server = ctx.message.server
    players[server.id].pause()

    if(len(queues[server.id]) > 0): 
        await client.say('Pausar låt.')
    else:
        await client.say('Ingen låt spelas.')

@client.command(pass_context = True)
async def resume(ctx):    
    print(str(ctx.message.author) + ' resumed song')
    server = ctx.message.server

    players[server.id].resume()
    
    if(len(queues[server.id]) > 0): 
        await client.say('Återupptar uppspelning av låt.')
    else:
        await client.say('Ingen låt är pausad.')

@client.command(pass_context = True)
async def search(ctx):
    server = ctx.message.server

    search = "+".join(ctx.message.content.split(" ")[1:])
    print(str(ctx.message.author) + ' searched for ' + search)

    results_tuple = scraper.scrape_yt(search)
    searches[server.id] = results_tuple[0]

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
    
    await client.send_message(author, embed=embed)

client.run(TOKEN)