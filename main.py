import discord
import youtube_dl

import responder
import token_reader as token

from discord.ext import commands

TOKEN = token.get_token()

client = commands.Bot(command_prefix = '!')
client.remove_command('help')

in_voice = False

players = {}
queues = {}

def check_queue(id):
    if queues[id] != []:
        queues[id].pop(0)
        queue_list = queues[id]
        player = queue_list[0]
        players[id] = player
        player.start()

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
    embed.add_field(name = '!stop', value = 'Stoppa låt', inline = False)
    embed.add_field(name = '!pause', value = 'Pausa låt', inline = False)
    embed.add_field(name = '!resume', value = 'Återuppta uppspelning av låt', inline = False)
    embed.add_field(name = '!skip', value = 'Spela nästa låt i kön', inline = False)
    
    await client.send_message(author, embed=embed)

@client.command(pass_context = True)
async def say(ctx):
    msg = '{0.author.mention}: '.format(ctx.message)
    msg += responder.process_message(ctx.message.content)
    await client.say(msg)

@client.event
async def on_ready():
    print('Bot is ready')

@client.command(pass_context = True)
async def play(ctx, url):
    global in_voice
    if not in_voice:
        channel = ctx.message.author.voice.voice_channel
        await client.join_voice_channel(channel)
        in_voice = True
    
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    song_url = url

    if url == 'despacito':
        song_url = responder.get_despacito()

    player = await voice_client.create_ytdl_player(song_url, after=lambda: check_queue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]

    
    if len(queues[server.id]) == 1:
        player.start()
        players[server.id] = player
        await client.say('Playing ' + song_url)
    else:
        await client.say(song_url + ' was added to the queue.\n%d songs are currently in the queue' % len(queues[server.id]))

@client.command(pass_context = True)
async def clear(ctx):
    server = ctx.message.server
    for player in queues[server.id]:
        player.stop()

    queues[server.id].clear()

    await client.say('There are currently %d songs in the queue.' % len(queues[server.id]))

@client.command(pass_context = True)
async def stop(ctx):    
    server = ctx.message.server
    players[server.id].stop()
    queues[server.id].pop(0)

    await client.say('Player stopped. There are still %d songs in the queue.' % len(queues[server.id]))

@client.command(pass_context = True)
async def skip(ctx):    
    server = ctx.message.server
    players[server.id].stop()
    check_queue(server.id)

    await client.say('Skipping song. There are %d songs left in the queue.' % len(queues[server.id]))

@client.command(pass_context = True)
async def pause(ctx):    
    server = ctx.message.server
    players[server.id].pause()

    await client.say('Pausing song.')

@client.command(pass_context = True)
async def resume(ctx):    
    server = ctx.message.server

    players[server.id].resume()
    await client.say('Resuming song.')

client.run(TOKEN)

