import discord
import datetime as dt
import random
import re
from discord.ext import commands
from collections import defaultdict
import asyncio
import time
import os
import webserver


DISCORD_TOKEN = os.environ['discordkey']
# intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
client = commands.Bot(command_prefix='!', intents=intents)

ARTY_ID = 548369997546782730
STAR_CHANNEL_ID = 1303737311720247297
message_count = {}
user_scores = {}
active_users = set()
balances = defaultdict(lambda: 1000)
predictions = {}


class Prediction:
    def __init__(self, question, options, creator, duration_seconds=3600):  # Default: 5 mins
        self.question = question
        self.options = options
        self.creator = creator
        self.bets = {}
        self.resolved = False
        self.winning_option = None
        self.deadline = time.time() + duration_seconds

    def place_bet(self, user_id, option_index, amount):
        if self.resolved:
            return "Prediction already resolved."
        if time.time() > self.deadline:
            return "Betting time is over for this prediction."
        if user_id in self.bets:
            return "You already placed a bet."
        if option_index >= len(self.options) or option_index < 0:
            return "Invalid option."
        if balances[user_id] < amount:
            return f"You don't have enough points. Your balance is {balances[user_id]}."

        balances[user_id] -= amount
        self.bets[user_id] = (option_index, amount)
        return f"Bet of {amount} placed on option {option_index + 1}."

    def resolve(self, winning_index):
        if self.resolved:
            return "Already resolved."
        self.resolved = True
        self.winning_option = winning_index

        total_pool = sum(amount for opt, amount in self.bets.values())
        winners = [uid for uid, (opt, _) in self.bets.items() if opt == winning_index]

        if not winners:
            return []

        total_winning_bets = sum(self.bets[uid][1] for uid in winners)

        for uid in winners:
            bet_amount = self.bets[uid][1]
            share = bet_amount / total_winning_bets
            payout = int(share * total_pool)
            balances[uid] += payout

        return winners


with open('Vile.txt', 'r', encoding='utf-8') as f: vile_ = f.readline()
with open('Lonely.txt', 'r', encoding='utf-8') as f: lonely_ = f.readline()
with open('pet.txt', 'r', encoding='utf-8') as f: pet_ = f.readline()
with open('Arabic.txt', 'r', encoding='utf-8') as f: arabic_ = f.readlines()
with open('tips.txt', 'r', encoding='utf-8') as f: tips_ = f.readlines()
with open('help.txt', 'r', encoding='utf-8') as f: help1 = f.readlines()
with open('Manifesto.txt', 'r', encoding='utf-8') as f:
    manifesto_ = f.readlines()
    manifesto_ = '\n'.join(manifesto_)
with open('truth.txt', 'r', encoding='utf-8') as f:
    truth_ = f.readlines()
    truth_ = '\n'.join(truth_)

with open('Necoarc_links.txt', 'r', encoding='utf-8') as f: neco_arc_images = f.readlines()


@client.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    if "i love you" in content_lower and client.user in message.mentions:
        image_url = 'https://c.tenor.com/6ZNgM9OQ8DgAAAAd/tenor.gif'

        embed = discord.Embed(color=discord.Color.dark_gray())
        embed.set_image(url=image_url)
        await message.channel.send(embed=embed)

    if "invincible" in content_lower or 'invisible' in content_lower:
        image_url = 'https://c.tenor.com/Q329gflKk7sAAAAC/tenor.gif'

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_image(url=image_url)
        await message.channel.send(embed=embed)

    if 'wtf' in content_lower or 'what the fuck' in content_lower:
        if message.author.id == ARTY_ID:
            if message.author not in message_count:
                message_count[message.author] = 2171
            message_count[message.author] += 1

    if random.randint(1, 1000) <= 3:
        await message.author.timeout(dt.timedelta(minutes=0.5))
        emoji = client.get_emoji(1359000758888038480)
        await message.channel.send(
            f"{message.author.display_name} stepped on a landmine. {emoji}\nTimed out for `30` seconds.")

    if 'sure' in content_lower:
        emoji1 = client.get_emoji(1356078124499992596)
        emoji2 = client.get_emoji(1359406795453632553)
        try:
            await message.add_reaction(random.choice([emoji1, emoji2]))
        except discord.HTTPException:
            print("Failed to react.")

    if 'stupid' in content_lower:
        emoji = client.get_emoji(1356090731067867197)
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            print("Failed to react.")

    if any([x in content_lower for x in ['faggot', 'nigga', 'nigger', 'retard']]):
        try:
            await message.add_reaction('🫃')
        except discord.HTTPException:
            print("Failed to react.")

    if any([x in content_lower.split() for x in ['hello', 'hi', 'ello', 'gm']]):
        try:
            await message.add_reaction('👋')
        except discord.HTTPException:
            print("Failed to react.")

    await client.process_commands(message)


@client.event
async def on_reaction_add(reaction, user):
    if user.id == 513573197283721226 and str(reaction.emoji) == "🔥":
        try:
            await reaction.message.add_reaction("🔥")
        except discord.HTTPException:
            print("Failed to react.")


@client.command()
async def wtf(ctx):
    member = client.get_user(ARTY_ID)
    count = message_count.get(member, 0)
    await ctx.send(f'Arty wrote wtf {count} times.')


@client.command()
async def quote(ctx):
    channel = client.get_channel(STAR_CHANNEL_ID)

    if not channel:
        await ctx.send("Channel not found!")
        return

    messages = [msg async for msg in channel.history(limit=500)]

    if messages:
        for i in range(100):
            message_link = str(random.choice(messages).content.split()[3])
            regex = r"https://discord\.com/channels/(\d+)/(\d+)/(\d+)"
            match = re.match(regex, message_link)
            if not match:
                return await ctx.send("Invalid link format.")
            guild_id, channel_id, message_id = map(int, match.groups())
            guild = client.get_guild(guild_id)
            if not guild:
                return await ctx.send("Guild not found.")
            channel = guild.get_channel(channel_id)
            if not channel:
                return await ctx.send("Channel not found.")
            message = await channel.fetch_message(message_id)
            if len(message.attachments) > 0:
                continue
            else:
                await ctx.send(f"{message.content}\n\n- {message.author.display_name}")
                break

    else:
        await ctx.send("No valid messages found!")


@client.command()
async def neco(ctx):
    image_url = random.choice(neco_arc_images)

    embed = discord.Embed(color=discord.Color.random())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


@client.command()
async def givecookie(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send("You cannot give cookies to yourself!")
        return

    if member not in user_scores:
        user_scores[member] = 0

    user_scores[member] += 1

    await ctx.send(
        f"{ctx.author.display_name} gave a cookie to {member.display_name}! {member.display_name} now has {user_scores[member]} cookies.")


@client.command()
async def cookiescore(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    score = user_scores.get(member, 0)
    await ctx.send(f"{member.display_name} has {score} cookies.")


@client.command()
async def vile(ctx):
    await ctx.send(vile_)


@client.command()
async def manifesto(ctx):
    await ctx.send(manifesto_)


@client.command()
async def lonely(ctx):
    await ctx.send(lonely_)


@client.command()
async def truth(ctx):
    await ctx.send(truth_)


@client.command()
async def pet(ctx):
    image_url = 'https://i.imgur.com/4iCIBOk.png'

    embed = discord.Embed(color=discord.Color.red())
    embed.set_image(url=image_url)
    await ctx.send(pet_, embed=embed)


@client.command()
async def skelet(ctx):
    image_url = 'https://i.imgur.com/BlZSRX5.png'

    embed = discord.Embed(color=discord.Color.light_gray())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


@client.command()
async def byesexual(ctx):
    image_url = 'https://i.redd.it/f9yypxdub0g91.gif'

    embed = discord.Embed(color=discord.Color.dark_gray())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


@client.command()
async def hugo(ctx):
    await ctx.send(f"{client.get_emoji(1188201048465219615)} :speech_balloon:")


@client.command()
async def latinx(ctx):
    image_url = 'https://c.tenor.com/fV6bL6Yt34MAAAAC/tenor.gif'

    embed = discord.Embed(color=discord.Color.dark_gray())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


@client.command()
async def yummers(ctx):
    image_url = 'https://c.tenor.com/jfaCPpAitzwAAAAd/tenor.gif'

    embed = discord.Embed(color=discord.Color.orange())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


@client.command()
async def greenhugo(ctx):
    image_url = 'https://media.discordapp.net/attachments/532964604683354112/1304482949332467804/EndingA_HUGOnodomek.png?ex=67f7492b&is=67f5f7ab&hm=88db764de87aee7757b19efd440f43da756f2c638f64683836165302aedde5a8&=&format=webp'

    embed = discord.Embed(color=discord.Color.brand_green())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)


@client.command()
async def knights(ctx):
    await ctx.send("8 armored knights on horseback rapidly approach your location\n\n⚔️🏇⚔️🏇⚔️🏇⚔️🏇⚔️🏇⚔️🏇⚔️🏇⚔️🏇")


@client.command()
async def arabic(ctx):
    no = random.randint(0, 28)
    await ctx.send(f"`There is an Arabic saying(№ {no + 1}):`\n> {arabic_[no * 3]} \n> {arabic_[no * 3 + 1]}")


@client.command()
async def arabicmeaning(ctx, no: int):
    await ctx.send(f"> {arabic_[(no - 1) * 3 + 2]}")


@client.command()
async def tip(ctx):
    # image_url = 'https://i.pinimg.com/originals/48/28/ba/4828ba780f4cbf3774f453a823124cd9.gif'
    #
    # embed = discord.Embed(color=discord.Color.dark_embed())
    # embed.set_image(url=image_url)

    no = random.randint(0, 16)
    await ctx.send(f"`Real world tip № {no}:`\n```{tips_[no]}```")


@client.command(name="create_prediction")
async def create_prediction(ctx, question: str, options: str, duration_seconds: int = 300):
    option_list = [opt.strip() for opt in options.split(',')]
    if len(option_list) < 2:
        await ctx.send("You need at least two options.")
        return

    predictions[ctx.channel.id] = Prediction(question, option_list, ctx.author, duration_seconds)
    await ctx.send(
        f"Prediction created: **{question}**\nOptions:\n" +
        "\n".join(f"{i}. {opt}" for i, opt in enumerate(option_list)) +
        f"\n\n⏳ You have {duration_seconds // 60} min(s) to place your bets!"
    )
    active_users.add(ctx.author.id)


@client.command(name="bet")
async def bet(ctx, option_number: int, amount: int):
    option_index = option_number - 1
    active_users.add(ctx.author.id)
    pred = predictions.get(ctx.channel.id)
    if not pred:
        await ctx.send("No active prediction in this channel.")
        return

    msg = pred.place_bet(ctx.author.id, option_index, amount)
    await ctx.send(msg)


@client.command(name="resolve_prediction")
async def resolve_prediction(ctx, winning_number: int):
    winning_index = winning_number - 1
    pred = predictions.get(ctx.channel.id)
    if not pred:
        await ctx.send("No active prediction to resolve.")
        return
    if ctx.author != pred.creator:
        await ctx.send("Only the prediction creator can resolve it.")
        return

    winners = pred.resolve(winning_index)
    if winners == "Already resolved.":
        await ctx.send("This prediction was already resolved.")
        return

    all_users = list(pred.bets.keys())
    losers = [uid for uid in all_users if uid not in winners]

    winner_mentions = ", ".join(f"<@{uid}>" for uid in winners) if winners else "Nobody"
    loser_mentions = ", ".join(f"<@{uid}>" for uid in losers) if losers else "Nobody"

    await ctx.send(
        f"Prediction resolved!\n🎉 **Winners**: {winner_mentions}\n💀 **Better luck next time**: {loser_mentions}")


@client.command(name="balance")
async def balance(ctx):
    bal = balances[ctx.author.id]
    await ctx.send(f"{ctx.author.mention}, your current balance is 💰 {bal} points.")


async def daily_bonus():
    while True:
        await asyncio.sleep(24 * 60 * 60)  # 24 hours

        if active_users:
            for uid in active_users:
                balances[uid] += 1000

            print(f"Granted +1000 daily bonus to {len(active_users)} users.")
            active_users.clear()


@client.event
async def on_ready():
    print(f"Bot is ready. Logged in as {client.user}")
    client.loop.create_task(daily_bonus())


@client.command()
async def help_(ctx):
    await ctx.send(''.join(help1))

webserver.keep_alive()
client.run(DISCORD_TOKEN)
