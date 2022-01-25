import discord
import random
import subprocess
import asyncio
import requests
import os
from discord.ext import commands, tasks
from wordle.wordle_result import WordleResult
from wordle.wordle_store import WordleStore
from datetime import date, time, datetime, timedelta

flat_file = os.getenv('wordle_bot_flat_file', "wordle.db")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=".", intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("wordle"))
    wordle_poster.start()
    print("Ready")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong! {} ms".format(round(bot.latency * 1000)))


@bot.command()
async def leaderboard(ctx, offset: int = 0):
    """
    Send the markdown leaderboard plus the top three string
    Args:
        offset (int): Week offset to pull previous weeks with
    """
    w = WordleStore(db=flat_file)

    await ctx.channel.send(w.get_markdown_leaderboard(offset=offset))
    top_three = w.get_top_three(offset=offset)
    if top_three:
        await ctx.channel.send(top_three)


@bot.event
async def on_message(message):
    result = WordleResult(message)

    if result.is_wordle_message():
        result.apply_score()
        await result.show()
    else:
        await bot.process_commands(message)


@bot.command()
@commands.has_role("admin")
async def reboot_bot(ctx):
    await ctx.channel.send("Pulling from git...")
    subprocess.Popen(["git", "pull", "origin", "master"]).wait()
    await ctx.channel.send("Rebooting...")
    p = subprocess.Popen(["python3", "wordle_bot.py"])

    try:
        p.wait(10)
    except subprocess.TimeoutExpired:
        await ctx.channel.send("Return Code OK")
        exit()

    await ctx.channel.send("Bot did not start")


async def get_dog():
    return requests.get("https://dog.ceo/api/breeds/image/random").json()["message"]


async def get_cat():
    return "https://cataas.com" + requests.get("https://cataas.com/cat?json=true").json()["url"]


async def send_pet_embed(ctx, pet_func):
    """
    Sends the pet func as an embed
    """
    await ctx.message.delete()
    embed = discord.Embed(description=ctx.message.content)
    petto = await pet_func()
    embed.set_image(url=petto)
    await ctx.channel.send(embed=embed)


@bot.command()
async def doggo(ctx):
    """
    Sends a random doggo photo as an embed
    """
    await send_pet_embed(ctx, get_dog)


@bot.command()
async def catto(ctx):
    """
    Sends a random catto photo as an embed
    """
    await send_pet_embed(ctx, get_cat)


async def post_wordle():
    """
    Posts the wordle link with a pet picture
    """
    image = await random.choice([get_dog, get_cat])()

    # wordle channel
    for channel in bot.channels:
        if channel.name == os.environ['wordle_bot_channel']:
            break
        else:
            channel = None

    if not channel:
        return

    message = discord.Embed(
        title="Wordle time!",
        description="Which one will it be this time?",
        url="https://www.powerlanguage.co.uk/wordle/"
    )
    message.set_image(url=image)

    await channel.send(embed=message)


@bot.command()
@commands.has_role("admin")
async def repost_wordle(ctx):
    """
    Repost the wordle link incase the previous one was bad
    """
    await ctx.message.delete()
    await post_wordle()


@tasks.loop(seconds=15)
async def wordle_poster():
    """
    Post the wordle link and a nice image just after every midnight
    """
    sleep_time = (datetime.combine(date.today() + timedelta(days=1), time.min) - datetime.now()).seconds
    # make sure it's 5 seconds after midnight because i hate the 11:59 posts
    await asyncio.sleep(sleep_time + 5)
    await bot.wait_until_ready()

    await post_wordle()

    # sleep for a few seconds so we don't accidentally double post
    await asyncio.sleep(2)


bot.run(os.environ['wordle_bot_token'])
