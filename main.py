import os
from typing import Dict
import discord
from discord.ext.commands import Bot
from tqdm import tqdm
import Image.make_image as make_image
from Image.emoji_loader import server_emojis
from Models.baseline import WCBaseline as WCModel
from preprocessing import resolve_tags, get_emojis
bot = Bot(command_prefix=";")
maxmsg = 1_000
# <server, wcmodel>
models: Dict[discord.Guild, WCModel] = {}
# <server, <emoji, count>>
emojis: Dict[discord.Guild, Dict[str, int]]


async def server_messages(server: discord.Guild):
	for channel in server.text_channels:
		# for every message in the channel up to a limit
		async for message in tqdm(channel.history(limit=maxmsg), desc=server.name, total=maxmsg):
			if not message.author.bot:
				yield message.author, message.content
			for reaction in message.reactions:
				reaction_str = str(reaction.emoji)
				for user in reaction.users():
					yield user, reaction_str


async def add_server(server: discord.Guild):
	messages = list(msg async for msg in server_messages(server))
	# create and train a new model
	models[server] = WCModel()
	models[server].train(messages)
	# count the emojis
	s_emojis = set(await server_emojis(server))
	emojis[server] = {e: 0 for e in s_emojis}
	for message in messages:
		for emoji in get_emojis(message, s_emojis):
			emojis[server][emoji] += 1


@bot.event
async def on_ready():
	for server in bot.guilds:
		await add_server(server)


@bot.event
async def on_guild_join(server: discord.Guild):
	await add_server(server)


@bot.command(name="cloud")
async def cloud(ctx):
	if isinstance(ctx.channel, discord.TextChannel):
		channelname = ctx.channel.guild.name + "#" + ctx.channel.name
	else:
		channelname = "DM"
	mentions = ctx.message.mentions
	if len(mentions) == 0:
		reqtext = "his WordCloud"
		mentions.append(ctx.author)
	else:
		reqtext = "a WordCloud for " + ", ".join([user.name + "#" + user.discriminator for user in mentions])
	print(f"{channelname}: {ctx.author.name}#{ctx.author.discriminator} requested {reqtext} !")
	server = ctx.channel.guild
	async with ctx.channel.typing():
		for member in mentions:
			image = make_image.wc_image(
				server,
				resolve_tags(server, models[server].word_cloud(member))
			)

			await ctx.channel.send(
				content=f"{member.mention}'s Word Cloud:", allowed_mentions=discord.AllowedMentions.none(),
				file=discord.File(fp=image, filename=f"{member.display_name}_word_cloud.png")
			)


try:
	with open("token.txt", "r") as ftoken:
		bot.run(ftoken.read())
except OSError:
	bot.run(os.environ["TOKEN"])
