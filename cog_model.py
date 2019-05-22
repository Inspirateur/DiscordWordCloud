from collections import Counter
from datetime import datetime, timedelta
import json
from time import time
from typing import Dict, List, Tuple, Set
import discord.ext.commands as commands
from discord import Activity, ActivityType, File, Message, Member
from Management import ignored
from WordCloudImage.make_image import virtual_image
from WordCloudModel.model import Model
try:
	from WordCloudModel.echo import Echo as ModelClass
except ImportError:
	from WordCloudModel.baseline import Baseline as ModelClass
puncmap = str.maketrans({',': ' ', '.': ' ', '\n': ' ', '—': ' ', ';': ' ', '’': '\''})


def resolve_tag(ctx, w: str) -> str:
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
					member = ctx.guild.get_member(int(user_id))
					if member is not None:
						return "@" + member.name
			elif w[1] == '#':
				# it's a channel tag, we resolve it
				channel = ctx.guild.get_channel(int(w[2:-1]))
				if channel is not None:
					return '#' + channel.name
			elif w[1] == ':':
				# it's probably an emoji
				emojisplit: List[str] = w[2:-1].split(':')
				if len(emojisplit) == 2 and emojisplit[1].isdigit():
					return f":{emojisplit[0]}:"
	return w


def resolve_words(ctx, wordcloud: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
	# resolve the tags
	tagresolved = []
	for (ngram, value) in wordcloud:
		tagresolved.append((" ".join([resolve_tag(ctx, w) for w in ngram.split(" ")]), value))
	return tagresolved


class ModelCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot
		self.model: Model = ModelClass()
		# a simple <word, <user, count>> used for misc commands
		self.words: Dict[str, Counter] = {}
		self.maxmsg: int = 20000
		self.maxdays: int = 120

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

	def add_to_model(self, msg: Message, n: int = 3):
		userid = str(msg.author.id)
		# split the message content with the most basic tokenization
		tokens: List = list(filter(bool, msg.content.lower().translate(puncmap).split(' ')))
		# add the content of the message as n-grams to echo
		for token in tokens:
			self.model.add(userid, token)
			if token not in self.words:
				self.words[token] = Counter()
			self.words[token][userid] += 1
		for i in range(2, n+1):
			for j in range(len(tokens)-i+1):
				self.model.add(userid, " ".join(tokens[j:j+i]), 1.5/n)

	async def load_from_discord(self):
		# the limit date, all read messages are after it
		deltalimit: timedelta = timedelta(days=self.maxdays)
		limitdate: datetime = datetime.now() - deltalimit
		print(f"READING START ({deltalimit.days} days limit, using {ModelClass.__name__})")
		start = time()
		# for every Guild
		for guild in self.bot.guilds:
			# get the member object representing the bot
			memberself = guild.me
			# get a set of ignored channel ids for this guild
			ignoredchans: Set[int] = set(ignored.ignore_list(guild.id))
			# for every readable channel
			for channel in guild.text_channels:
				if channel.permissions_for(memberself).read_messages:
					cstart = time()
					print(f"{channel.guild.name}#{channel.name} ... ", end='')
					if channel.id in ignoredchans:
						print("IGNORED")
					else:
						# for every message in the channel after the limit date, from new to old
						message = None
						count = 0
						async for message in channel.history(limit=self.maxmsg, after=limitdate, oldest_first=False):
							count += 1
							if not message.author.bot:
								self.add_to_model(message)
							# also add the reactions to echo if there's any
							for reaction in message.reactions:
								async for user in reaction.users():
									self.model.add(str(user.id), str(reaction.emoji))
						if message is not None and count >= self.maxmsg:
							warning = f"  /!\\ max msg reached, could only read {(datetime.now() - message.created_at).days} days"
						else:
							warning = ""
						print(f"done ({round(time() - cstart, 2)} sec | {count} msg){warning}")
		print(f"READING OVER ({round(time() - start, 1)} sec)")
		self._save()

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Logged on as {self.bot.user}!")
		try:
			self._load()
		except FileNotFoundError:
			self.model = ModelClass()
			self.words = {}
			await self.bot.change_presence(activity=Activity(name="your messages", type=ActivityType.watching))
			await self.load_from_discord()
		await self.bot.change_presence(activity=Activity(name=self.bot.command_prefix+"cloud", type=ActivityType.listening))
		print("Ready")

	@commands.command(brief="- Request your or other's word cloud !")
	async def cloud(self, ctx):
		print(f"{ctx.author.name}#{ctx.author.discriminator} requested a wordcloud !")
		mentions: List[Member] = ctx.message.mentions
		if len(mentions) == 0:
			mentions.append(ctx.author)
		async with ctx.channel.typing():
			for member in mentions:
				image = virtual_image(resolve_words(ctx, self.model.word_cloud(str(member.id), n=2)))
				await ctx.channel.send(
					content=f"**{member.display_name}**'s Word Cloud ({ModelClass.__name__}):",
					file=File(fp=image, filename=f"{member.display_name}_word_cloud.png")
				)
