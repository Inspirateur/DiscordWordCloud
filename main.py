import os
import sys
from typing import Dict
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext.commands import Bot
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import Image.make_image as make_image
from Image.emoji_loader import EmojiResolver
from Models.baseline import WCBaseline as WCModel
from preprocessing import resolve_tags, get_emojis
intents = discord.Intents.default()
intents.members = True
intents.emojis = True
bot = Bot(command_prefix=";", intents=intents)
maxmsg = 10_000
# <server, wcmodel>
models: Dict[discord.Guild, WCModel] = {}
# <server, <emoji, count>>
emojis: Dict[discord.Guild, Dict[str, int]] = {}
emoji_resolver = None


async def server_messages(server: discord.Guild) -> list:
	messages = []
	for channel in tqdm(server.text_channels, desc="Channels", file=sys.stdout):
		if channel.permissions_for(server.me).read_messages:
			# for every message in the channel up to a limit
			async for message in tqdm_asyncio(
					channel.history(limit=maxmsg), desc=channel.name, total=maxmsg, file=sys.stdout, leave=False
			):
				if not message.author.bot:
					messages.append((message.author, message.content))
				for reaction in message.reactions:
					reaction_str = str(reaction.emoji)
					async for user in reaction.users():
						messages.append((user, reaction_str))
	return messages


async def add_server(server: discord.Guild):
	print(f"Adding {server.name}")
	messages = await server_messages(server)
	# create and train a new model
	models[server] = WCModel()
	models[server].train(messages)
	# count the emojis
	s_emojis = set(str(emoji) for emoji in server.emojis)
	emojis[server] = {e: 0 for e in s_emojis}
	for _, message in messages:
		for emoji in get_emojis(message, s_emojis):
			emojis[server][emoji] += 1
	print()


@bot.event
async def on_ready():
	global emoji_resolver
	emoji_resolver = EmojiResolver(bot)
	await emoji_resolver.load_server_emojis()
	for server in bot.guilds:
		await add_server(server)
	print("Ready")


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
			image = await make_image.wc_image(
				resolve_tags(server, models[server].word_cloud(member)),
				emoji_resolver
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
