from asyncio.tasks import create_task
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Union

import discord.ext.commands as commands
from discord import Activity, ActivityType, Emoji, File, Guild, Member, Message, Reaction, TextChannel, User

from Image.emoji_loader import EmojiLoader
import Image.make_image as make_image
import Management.ignored as ignored
from NLP.discord_nlp import Token, tokenize, ngrams, ngramslower, resolve_tags
from NLP.Models.model import Model
try:
	from NLP.Models.echo import Echo as ModelClass
except ImportError as e:
	print(e)
	from NLP.Models.baseline import Baseline as ModelClass


class Cloud(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot
		self.wrdmodel: Model = ModelClass()
		self.emomodel: Model = ModelClass()
		try:
			ModelClass().add_n("", ("", ))
			self.n = 3
			print(f"{ModelClass.__name__} handles n-grams, we use n=3")
		except (NotImplementedError, AttributeError):
			self.n = 1
			print(f"{ModelClass.__name__} doesn't handle n-grams, we use n=1")
		self.emojis: Dict[int, Emoji] = {}
		# a simple <guildID, <word, <user, count>>> used for misc commands
		self.words: Dict[int, Dict[Union[Tuple, str], Counter]] = {}
		self.wordsn: int = 3
		self.maxmsg: int = 20000
		self.maxdays: int = 120
		self.limitdate: datetime = datetime.now() - timedelta(days=self.maxdays)

	def add_to_model(self, msg: Message):
		userid = str(msg.author.id)
		guildid = msg.guild.id
		# tokenize the sentence
		tokens: List[Token] = tokenize(msg.content)
		# create one list with only words, one with only emojis and one mixed
		words: List[str] = []
		emos: List[str] = []
		mixed: List[str] = []
		for token in tokens:
			# FIXME: I don't know why PyCharm highlights .data in yellow, probably a PyCharm bug
			# 	https://youtrack.jetbrains.com/issue/PY-36288
			mixed.append(token.data)
			emos.append(token.data) if token.is_emoji else words.append(token.data)
		# fill self.words
		for ngram in ngramslower(mixed, n=self.wordsn):
			if ngram not in self.words:
				self.words[guildid][ngram] = Counter()
			self.words[guildid][ngram][userid] += 1
		# fill self.emomodel
		for emo in emos:
			self.emomodel.add(userid, emo)
		# fill self.wrdmodel
		for word in words:
			self.wrdmodel.add(userid, word)
		for i in range(2, self.n+1):
			for igram in ngrams(words, i):
				self.wrdmodel.add_n(userid, igram)

	async def load_msgs(self, guild: Guild) -> None:
		print(f"Start reading messages for {guild.name}")
		if guild.id not in self.words:
			self.words[guild.id] = {}
		# get the member object representing the bot
		memberself = guild.me
		# get a set of ignored channel ids for this guild
		ignoredchans: Set[int] = set(ignored.ignore_list(guild.id))
		# for every readable channel
		for channel in guild.text_channels:
			# if we can and must read the channel
			if channel.permissions_for(memberself).read_messages and channel.id not in ignoredchans:
				# for every message in the channel after the limit date, from new to old
				async for message in channel.history(limit=self.maxmsg, after=self.limitdate, oldest_first=False):
					# add the message to the model if it's not from a bot
					if not message.author.bot:
						self.add_to_model(message)
					# also add the reactions to the model if there's any
					for reaction in message.reactions:
						async for user in reaction.users():
							emoji = str(reaction.emoji)
							user_id = str(user.id)
							self.emomodel.add(user_id, emoji)
							if emoji not in self.words[guild.id]:
								self.words[guild.id][emoji] = Counter()
							self.words[guild.id][emoji][user_id] += 1
		print(f"Finished reading messages for {guild.name}")

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Logged on as {self.bot.user}!")
		# for every Guild
		for guild in self.bot.guilds:
			# start a parallel guild emoji loader
			emoloader = EmojiLoader(guild, make_image.emo_imgs)
			emoloader.start()
			# start a parallel guild message loader
			create_task(self.load_msgs(guild))
		await self.bot.change_presence(activity=Activity(name=self.bot.command_prefix+"cloud", type=ActivityType.listening))

	@commands.Cog.listener()
	async def on_guild_join(self, guild: Guild):
		print(f">>> Joined the guild {guild.name} !")
		create_task(self.load_msgs(guild))

	@commands.Cog.listener()
	async def on_message(self, msg: Message):
		# check if the author of the message is not a bot and if the channel is not ignored
		if not msg.author.bot and isinstance(msg.channel, TextChannel) and \
				msg.channel.id not in ignored.ignore_list(msg.guild.id):
			self.add_to_model(msg)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction: Reaction, user: User):
		# check if the author of the reaction is not a bot and if the channel is not ignored
		if not user.bot and reaction.message.channel.id not in ignored.ignore_list(reaction.message.guild.id):
			emoji = str(reaction.emoji)
			user_id = str(user.id)
			# add the emoji to the model
			self.emomodel.add(user_id, emoji)
			# add the emoji to words
			if emoji not in self.words[reaction.message.guild.id]:
				self.words[reaction.message.guild.id][emoji] = Counter()
			self.words[reaction.message.guild.id][emoji][user_id] += 1

	@commands.command(brief="- Request your or other's word cloud !")
	async def cloud(self, ctx):
		if isinstance(ctx.channel, TextChannel):
			channelname = ctx.channel.guild.name+"#"+ctx.channel.name
		else:
			channelname = "DM"
		mentions: List[Member] = ctx.message.mentions
		if len(mentions) == 0:
			reqtext = "his WordCloud"
			mentions.append(ctx.author)
		else:
			reqtext = "a WordCloud for " + ", ".join([user.name+"#"+user.discriminator for user in mentions])
		print(f"{channelname}: {ctx.author.name}#{ctx.author.discriminator} requested {reqtext} !")
		async with ctx.channel.typing():
			for member in mentions:
				image = make_image.simple_image(resolve_tags(ctx, self.wrdmodel.word_cloud(str(member.id), n=2)))
				await ctx.channel.send(
					content=f"**{member.display_name}**'s Word Cloud ({ModelClass.__name__}):",
					file=File(fp=image, filename=f"{member.display_name}_word_cloud.png")
				)
