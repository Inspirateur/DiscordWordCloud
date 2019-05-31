from asyncio.tasks import create_task
from collections import Counter, deque
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Set, Tuple, Union

import discord.ext.commands as commands
from discord import Activity, ActivityType, Emoji, File, Guild, Member, Message, Reaction, TextChannel, User

from emoji_loader import EmojiLoader
import Image.make_image as make_image
import Management.ignored as ignored
from Model.model import Model
try:
	from Model.echo import Echo as ModelClass
except ImportError:
	from Model.baseline import Baseline as ModelClass
globreg = re.compile(r'(<a?:[^:]+:[0-9]+>)|https?://(?:www.)?([^/\s]+)[^\s]+|(<..?[0-9]+>)|([\w-]+)|([^\s])')


class Cloud(commands.Cog):
	# 	TODO: Do a proper discord message tokenization module somewhere else,
	# 	 that given a message content returns a list of custom Token object, with (among other) the attribute "is_emoji"
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot
		self.model: Model = ModelClass()
		try:
			ModelClass().add_n("", ("", ))
			self.n = 3
			print(f"{ModelClass.__name__} handles n-grams, we use n=3")
		except (NotImplementedError, AttributeError):
			self.n = 1
			print(f"{ModelClass.__name__} doesn't handle n-grams, we use n=1")
		self.emojis: Dict[int, Emoji] = {}
		# a simple <guildID, <word, <user, count>>> used for misc commands
		self.words: Dict[int, Dict[str, Counter]] = {}
		self.wordsn: int = 3
		self.maxmsg: int = 20000
		self.maxdays: int = 120
		self.limitdate: datetime = datetime.now() - timedelta(days=self.maxdays)

	def _save(self):
		with open(f"WordCloudModel/{ModelClass.__name__}_save.json", "w") as fjson:
			fjson.write(self.model.serialize())
			print(f"{ModelClass.__name__} saved")
		with open(f"WordCloudModel/words_save.json", "w") as wjson:
			wjson.write(json.dumps(self.words))
			print("words saved")

	def _load(self):
		with open(f"WordCloudModel/{ModelClass.__name__}_save.json", "r") as fjson:
			self.model = ModelClass.parse(fjson.read())
		with open(f"WordCloudModel/words_save.json", "r") as wjson:
			self.words = json.load(wjson)
		print(f"{ModelClass.__name__} loaded from save")
		print("words loaded from save")

	def add_to_model(self, msg: Message):
		userid = str(msg.author.id)
		guilid = msg.guild.id
		lasttokens = deque(maxlen=self.wordsn)
		# build the list of tokens without the emojis
		tokens: List[str] = []
		# for every token in the message
		for match in globreg.findall(msg.content):
			# try to look for emoji in the match
			emoji = match[0]
			if emoji:
				lasttokens.append(emoji)
				# add the emoji to the model
				self.model.add(userid, emoji)
			else:
				# the match is not an emoji, we look for a token
				token = ''.join(match[1:]).lower()
				if token:
					lasttokens.append(token)
					# add the token
					tokens.append(token)
			if len(lasttokens) == self.wordsn:
				# we start adding n-grams to words only when lasttoken deque is full
				for i in range(len(lasttokens)):
					igram = " ".join([lasttokens[j] for j in range(i + 1)])
					if igram not in self.words:
						self.words[guilid][igram] = Counter()
					self.words[guilid][igram][userid] += 1
		# if the lasttokens deque is smaller than maximum, we must add the n-grams to words now
		if len(lasttokens) < self.wordsn:
			for i in range(len(lasttokens)):
				igram = " ".join([lasttokens[j] for j in range(i + 1)])
				if igram not in self.words[guilid]:
					self.words[guilid][igram] = Counter()
				self.words[guilid][igram][userid] += 1

		# add the tokens individually to the model
		for word in tokens:
			self.model.add(userid, word)
		# add the tokens as n-grams (n>=2) to the model
		for i in range(2, self.n + 1):
			for j in range(len(tokens) - i + 1):
				self.model.add_n(userid, tuple(tokens[j:j + i]), 1.0 / self.n)

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
					if not message.author.bot:
						self.add_to_model(message)
					# also add the reactions to echo if there's any
					for reaction in message.reactions:
						async for user in reaction.users():
							emoji = str(reaction.emoji)
							user_id = str(user.id)
							self.model.add(user_id, emoji)
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
			self.model.add(user_id, emoji)
			# add the emoji to words
			if emoji not in self.words[reaction.message.guild.id]:
				self.words[reaction.message.guild.id][emoji] = Counter()
			self.words[reaction.message.guild.id][emoji][user_id] += 1

	def resolve_tag(self, ctx, w: str) -> Union[str, Emoji]:
		if len(w) > 3:
			if w.startswith("<") and w.endswith(">"):
				if w[1] == '@':
					if w[2] == '&':
						# it's a role tag, we resolve it
						role = ctx.guild.get_role(int(w[3:-1]))
						if role is not None:
							return "@" + role.name
					else:
						# it's a user tag, we resolve it
						if w[2] == '!':
							user_id = w[3:-1]
						else:
							user_id = w[2:-1]
						member: Member = ctx.guild.get_member(int(user_id))
						if member is not None:
							return "@" + member.name
				elif w[1] == '#':
					# it's a channel tag, we resolve it
					channel = ctx.guild.get_channel(int(w[2:-1]))
					if channel is not None:
						return '#' + channel.name
				elif w[1] == ':' or w[1] == 'a':
					# it's probably an emoji
					emojisplit: List[str] = w[:-1].split(':')
					if len(emojisplit) == 3:
						try:
							# try to get the emoji from its ID
							emoji: Emoji = self.bot.get_emoji(int(emojisplit[2]))
							if emoji is not None:
								# we got one, return the emoji object
								return emoji
							else:
								# we couldn't get it, raise key error
								raise KeyError
						except ValueError:
							pass
		return w

	def resolve_words(self, ctx, wordcloud: List[Tuple[str, float]]) -> List[Tuple[Union[str, Emoji], float]]:
		if not isinstance(ctx.channel, TextChannel):
			return wordcloud
		# resolve the tags
		tagresolved = []
		for (ngram, value) in wordcloud:
			try:
				words = ngram.split(" ")
				if len(words) == 1:
					tagresolved.append((self.resolve_tag(ctx, words[0]), value))
				else:
					tagresolved.append((" ".join([self.resolve_tag(ctx, w) for w in words]), value))
			except KeyError:
				pass
		return tagresolved

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
				image = make_image.simple_image(self.resolve_words(ctx, self.model.word_cloud(str(member.id), n=2)))
				await ctx.channel.send(
					content=f"**{member.display_name}**'s Word Cloud ({ModelClass.__name__}):",
					file=File(fp=image, filename=f"{member.display_name}_word_cloud.png")
				)
