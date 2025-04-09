import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
import asyncio
import datetime
import time

active_users = set()

balances = defaultdict(lambda: 1000)  # Every user starts with 1000 points

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Stores active predictions
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
        return f"Bet of {amount} placed on option {option_index}."

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


@bot.command(name="create_prediction")
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


@bot.command(name="bet")
async def bet(ctx, option_index: int, amount: int):
    active_users.add(ctx.author.id)
    pred = predictions.get(ctx.channel.id)
    if not pred:
        await ctx.send("No active prediction in this channel.")
        return

    msg = pred.place_bet(ctx.author.id, option_index, amount)
    await ctx.send(msg)


@bot.command(name="resolve_prediction")
async def resolve_prediction(ctx, winning_index: int):
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


@bot.command(name="balance")
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


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    bot.loop.create_task(daily_bonus())


# Replace 'YOUR_TOKEN_HERE' with your bot's token
bot.run('MTM1NzczMzA0MDYxNjUwNTQ4NQ.GmB0Tn.v89DDcZJhGo4_8pr6HB02n0S2_nyLQb8o1VDYM')
