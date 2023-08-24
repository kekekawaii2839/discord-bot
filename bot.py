import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, FFmpegOpusAudio

import os
import asyncio
 
intents = discord.Intents.all()
intents.voice_states = True

proxy = 'http://127.0.0.1:7890'

bot = commands.Bot(command_prefix='!', intents=intents, proxy=proxy)
token = os.environ.get('DISCORD_BOT_TOKEN')

playlist = []
#read local .opus files and add to playlist
current_dir = os.path.dirname(os.path.abspath(__file__))
for file in os.listdir(current_dir):
    if file.endswith('.opus'):
        playlist.append(file)

play_index = 0

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(pass_context=True)
async def join(ctx):
    print('join')
    if ctx.author.voice is None:
        await ctx.send('You are not connected to a voice channel')
        return
    vc = ctx.author.voice.channel
    if ctx.voice_client is None:
        await vc.connect()
    else:
        await ctx.voice_client.move_to(vc)

@bot.command(pass_context=True)
async def play(ctx):
    if ctx.voice_client is None:
        await ctx.send('I am not connected to a voice channel')
        return
    while True:
        global play_index
        await _play(ctx, playlist[play_index])
        while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await asyncio.sleep(1)
        play_index += 1
        if play_index >= len(playlist):
            play_index = 0

async def _play(ctx, url: str):
    print('_play')
    source = FFmpegOpusAudio(playlist[play_index], bitrate=96)
    player = ctx.voice_client.play(source, bitrate=96, signal_type='music')

@bot.command(pass_context=True)
async def stop(ctx):
    print('stop')
    await ctx.voice_client.disconnect()

@bot.command(pass_context=True)
async def pause(ctx):
    print('pause')
    ctx.voice_client.pause()

@bot.command(pass_context=True)
async def resume(ctx):
    print('resume')
    ctx.voice_client.resume()

@bot.command(pass_context=True)
async def refresh_playlist(ctx):
    print('refresh_playlist')
    global play_index
    tmp_url = playlist[play_index]
    playlist.clear()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(current_dir):
        if file.endswith('.opus'):
            playlist.append(file)
    play_index = playlist.index(tmp_url)
    if play_index not in range(len(playlist)):
        play_index = 0
    await ctx.send('Playlist refreshed')

bot.run(token=token)