import csv
import json
import os
import sys
import traceback
from typing import Dict, List
from datetime import datetime, timedelta
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext.commands import Bot, has_permissions, MissingPermissions, guild_only, NoPrivateMessage
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
MAX_MESSAGES = 10_000
DEFAULT_DAYS = 50
# <server, wcmodel>
_models: Dict[discord.Guild, WCModel] = {}
# <server, <emoji, count>>
_emojis: Dict[discord.Guild, Dict[str, int]] = {}
_emoji_resolver: EmojiResolver = None
# TODO: would be nice to bundle it into an .exe but it seems pyinstaller is not able to do it yet


async def server_messages(server: discord.Guild, to_edit: discord.Message, days) -> list:
	date_after = datetime.now()-timedelta(days=days)
	messages = []
	# get all readable channels
	channels: List[discord.TextChannel] = list(filter(
		lambda c: c.permissions_for(server.me).read_messages,
		server.text_channels
	))
	for i, channel in tqdm(list(enumerate(channels)), desc=f"Channels {server.name}", ncols=140, file=sys.stdout):
		await to_edit.edit(content=f"> Reading {channel.mention} ({i+1}/{len(channels)})")
		# for every message in the channel up to a limit
		async for message in tqdm_asyncio(
				channel.history(limit=MAX_MESSAGES, after=date_after), desc=channel.name,
				total=MAX_MESSAGES, ncols=140, file=sys.stdout, leave=False
		):
			if not message.author.bot:
				messages.append((message.author.id, message.content))
			for reaction in message.reactions:
				reaction_str = str(reaction.emoji)
				async for user in reaction.users():
					messages.append((user.id, reaction_str))
	return messages


async def add_server(server: discord.Guild, messages):
	# create and train a new model
	_models[server] = WCModel()
	_models[server].train(messages)
	# count the emojis
	s_emojis = set(str(emoji) for emoji in server.emojis)
	_emojis[server] = {e: 0 for e in s_emojis}
	for _, message in messages:
		for emoji in get_emojis(message, s_emojis):
			_emojis[server][emoji] += 1


@bot.event
async def on_ready():
	global _emoji_resolver
	_emoji_resolver = EmojiResolver(bot)
	await _emoji_resolver.load_server_emojis()
	print("Ready")


@bot.event
async def on_guild_join(server: discord.Guild):
	global _emoji_resolver
	await _emoji_resolver.load_server_emojis(server)


@bot.command(name="load", brief=f"Reads the messages of this server up to x days (cap at {MAX_MESSAGES} per channel)")
@guild_only()
@has_permissions(manage_channels=True)
async def load(ctx, days=None):
	if days is None:
		days = DEFAULT_DAYS
	else:
		try:
			days = int(days)
		except ValueError:
			await ctx.channel.send(f"`{days}` is not an integer, defaulting to {DEFAULT_DAYS}")
			days = DEFAULT_DAYS
	await ctx.channel.send(f"Loading messages up to {days} days")
	to_edit = await ctx.channel.send(".")
	status = await ctx.channel.send("**. . .**")
	server = ctx.message.channel.guild
	messages = await server_messages(server, to_edit, days)
	# we save messages for fast reloading
	with open(f"save_{server.id}.csv", "w") as fmessages:
		csv.writer(fmessages).writerows(messages)
	await add_server(server, messages)
	await status.edit(content="Done !")


@load.error
async def load_error(ctx, error):
	if isinstance(error, MissingPermissions):
		await ctx.channel.send(
			f"Sorry {ctx.message.author.mention} you need manage channels permission to use this command.",
			allowed_mentions=discord.AllowedMentions.none()
		)
	elif isinstance(error, NoPrivateMessage):
		await ctx.channel.send("This command can only be used in a server channel.")
	else:
		traceback.print_exc()


@bot.command(name="reload", brief=f"Reload the last state, for debugging")
@guild_only()
@has_permissions(manage_channels=True)
async def reload(ctx):
	await ctx.channel.send(f"Reloading the last state ...")
	server = ctx.message.channel.guild
	with open(f"save_{server.id}.csv", "r") as fmessages:
		reader = csv.reader(fmessages)
		messages = [(int(line[0]), line[1]) for line in reader]
	await add_server(server, messages)
	await ctx.channel.send("Done !")


@reload.error
async def reload_error(ctx, error):
	if isinstance(error, MissingPermissions):
		await ctx.channel.send(
			f"Sorry {ctx.message.author.mention} you need manage channels permission to use this command.",
			allowed_mentions=discord.AllowedMentions.none()
		)
	elif isinstance(error, NoPrivateMessage):
		await ctx.channel.send("This command can only be used in a server channel.")
	elif isinstance(error, OSError):
		await ctx.channel.send("Found no saves to reload, use `;load` instead.")
	else:
		traceback.print_exc()


@bot.command(name="cloud", brief="Creates a workcloud for you or whoever you tag")
@guild_only()
async def cloud(ctx, *args):
	server: discord.Guild = ctx.channel.guild
	if server not in _models:
		await ctx.channel.send(
			"Word Clouds are not ready for this server yet, either call `;load` if you haven't already or wait for it to finish."
		)
		return
	# get all unique members targeted in this command
	members = set(ctx.message.mentions)
	for user_id in args:
		try:
			member = server.get_member(int(user_id))
			if member:
				members.add(member)
		except ValueError:
			pass
	# if there's none it's for the author of the command
	if not members:
		members.add(ctx.message.author)
	async with ctx.channel.typing():
		for member in members:
			wc = _models[server].word_cloud(member.id)
			if not wc:
				await ctx.channel.send(
					content=f"Sorry I don't have any data on {member.mention} ...",
					allowed_mentions=discord.AllowedMentions.none()
				)
				continue
			image = await make_image.wc_image(
				resolve_tags(server, wc),
				_emoji_resolver
			)

			await ctx.channel.send(
				content=f"{member.mention}'s Word Cloud:", allowed_mentions=discord.AllowedMentions.none(),
				file=discord.File(fp=image, filename=f"{member.display_name}_word_cloud.png")
			)


@cloud.error
async def cloud_error(ctx, error):
	if isinstance(error, NoPrivateMessage):
		await ctx.channel.send("This command can only be used in a server channel")
	else:
		traceback.print_exc()


def emoji_usage_list(emo_count):
	# compute a total for normalisation
	total = sum(emo_count.values())
	# convert to list of tuple and sort
	emo_count = sorted(list(emo_count.items()), key=lambda kv: kv[1], reverse=True)
	# separate the top 5 and the bottom 5
	txtlist = []
	if len(emo_count) > 20:
		top = emo_count[:10]
		bottom = emo_count[-10:]
		for (emoji, count) in top:
			txtlist.append(f"\t{emoji} {count / total:.1%}")
		txtlist.append("...")
		for (emoji, count) in bottom:
			txtlist.append(f"\t{emoji} {count / total:.1%}")
	else:
		for (emoji, count) in emo_count:
			txtlist.append(f"\t{emoji} {count / total:.1%}")
	return txtlist


@bot.command(name="emojis", brief="Displays the emoji usage of this server")
@guild_only()
async def emojis(ctx):
	server = ctx.channel.guild
	if server not in _emojis:
		await ctx.channel.send(
			"Emoji usage is not ready for this server yet, either call `;load` if you haven't already or wait for it to finish."
		)
		return
	global_emo_count = _emojis[server]
	emo_count = {}
	animated_count = {}
	for emo, count in global_emo_count.items():
		if emo.startswith("<a"):
			animated_count[emo] = count
		else:
			emo_count[emo] = count
	txt_list = emoji_usage_list(emo_count)
	if txt_list:
		await ctx.channel.send(f"Emoji usage for this server:\n" + "\n".join(txt_list))
	else:
		await ctx.channel.send("Emoji usage for this server:\nIt's empty.")
	txt_list = emoji_usage_list(animated_count)
	if txt_list:
		await ctx.channel.send(f"Animated emoji usage for this server:\n" + "\n".join(txt_list))
	else:
		await ctx.channel.send("Animated emoji usage for this server:\nIt's empty.")


@emojis.error
async def emojis_error(ctx, error):
	if isinstance(error, NoPrivateMessage):
		await ctx.channel.send("This command can only be used in a server channel")
	else:
		traceback.print_exc()


@bot.command(name="info")
async def info(ctx):
	await ctx.channel.send(f"Author: Inspi#8989\nCode: https://github.com/Inspirateur/DiscordWordCloud")


try:
	with open("token.txt", "r") as ftoken:
		bot.run(ftoken.read())
except OSError as e:
	print("Could not open the token file:", e)
	bot.run(os.environ["TOKEN"])
