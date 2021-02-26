import os
from typing import Dict
import discord
from discord.ext.commands import Bot
from tqdm import tqdm
import Image.make_image as make_image
from Image.emoji_loader import load_guild_emojis
from Models.baseline import WCBaseline as WCModel
from preprocessing import resolve_tags
bot = Bot(command_prefix=";")
maxmsg = 1_000
# <server, wcmodel>
models: Dict[str, WCModel] = {}


async def messages(server: discord.Guild):
	for channel in server.text_channels:
		# for every message in the channel up to a limit
		async for message in tqdm(channel.history(limit=maxmsg), desc=server.name, total=maxmsg):
			if not message.author.bot:
				yield message.author.id, message.content
			for reaction in message.reactions:
				reaction_str = str(reaction.emoji.id)
				for user in reaction.users():
					yield user.id, reaction_str


async def add_server(server: discord.Guild):
	# load the custom emojis
	await load_guild_emojis(server, make_image.emo_imgs)
	# create and train a new model
	models[server.id] = WCModel()
	models[server.id].train(list(msg async for msg in messages(server)))


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
	server = ctx.channel.guild.id
	async with ctx.channel.typing():
		for member in mentions:
			image = make_image.wc_image(
				resolve_tags(server, models[server.id].word_cloud(str(member.id)))
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
