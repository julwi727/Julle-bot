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
            client.say('Now playing: ' + player.url)
        else:
            client.say('No more songs in queue.')
    

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
    print('play(ctx, url)')
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
    
    print('currently %d songs in the queue ' % len(queues[server.id]))
    if len(queues[server.id]) == 1:
        players[server.id] = player

        player.start()
        await client.say('Playing ' + song_url)
    else:
        await client.say(song_url + ' was added to the queue.\nThere are currently %d songs in the queue' % len(queues[server.id]))

@client.command(pass_context = True)
async def clear(ctx):
    print('clear(ctx)')
    server = ctx.message.server
    for player in queues[server.id]:
        player.stop()

    if(len(queues[server.id]) > 0):
        queues[server.id].clear()
        players[server.id] = None
        await client.say('There are currently %d songs in the queue.' % len(queues[server.id]))
    else:
        await client.say('There are no songs in the queue.')

@client.command(pass_context = True)
async def skip(ctx):
    print('skip(ctx)')
    server = ctx.message.server
    print('currently %d songs in the queue ' % len(queues[server.id]))
    players[server.id].stop()
    print('currently %d songs in the queue ' % len(queues[server.id]))
    
    if(len(queues[server.id]) > 0): 
        await client.say('Skipping song.')
        await client.say('Now playing: ' + players[server.id].url)
    else:
        await client.say('There are no songs in the queue.')
    

@client.command(pass_context = True)
async def pause(ctx):    
    print('pause(ctx)')
    server = ctx.message.server
    players[server.id].pause()

    if(len(queues[server.id]) > 0): 
        await client.say('Pausing song.')
    else:
        await client.say('No song is playing.')

@client.command(pass_context = True)
async def resume(ctx):    
    print('resume(ctx)')
    server = ctx.message.server

    players[server.id].resume()
    
    if(len(queues[server.id]) > 0): 
        await client.say('Resuming song.')
    else:
        await client.say('No song is paused.')


client.run(TOKEN)

