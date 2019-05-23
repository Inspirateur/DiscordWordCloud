from asyncio.tasks import create_task
from collections import Counter
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Union
import discord.ext.commands as commands
from discord import Activity, ActivityType, Emoji, File, Member, TextChannel
from emoji_loader import EmojiLoader
from message_loader import load_msgs
import WordCloudImage.make_image as make_image
from WordCloudModel.model import Model
try:
	from WordCloudModel.echo import Echo as ModelClass
except ImportError:
	from WordCloudModel.baseline import Baseline as ModelClass


class Cloud(commands.Cog):
	# TODO: implement basic real time training (compatible with save/load):
	# 	if there's no save: train, and save with the date of the last read message
	# 	if there a save: get the date of last read message, and complete the training from there
	# 	after that: listen to messages and simply use add_to_model
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot
		self.model: Model = ModelClass()
		self.emojis: Dict[int, Emoji] = {}
		# a simple <guildID, <word, <user, count>>> used for misc commands
		self.words: Dict[int, Dict[str, Counter]] = {}
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

	async def load_from_discord(self):
		# for every Guild
		for guild in self.bot.guilds:
			# start a parallel message loader
			self.words[guild.id] = {}
			create_task(load_msgs(guild, self.model, self.words[guild.id], self.limitdate, self.maxmsg))

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Logged on as {self.bot.user}!")
		# for every Guild
		for guild in self.bot.guilds:
			# start a parallel emoji loader
			emoloader = EmojiLoader(guild, make_image.emo_imgs)
			emoloader.start()
		self.model = ModelClass()
		self.words = {}
		await self.load_from_discord()
		await self.bot.change_presence(activity=Activity(name=self.bot.command_prefix+"cloud", type=ActivityType.listening))

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		self.words[guild.id] = {}
		create_task(load_msgs(guild, self.model, self.words[guild.id], self.limitdate, self.maxmsg))

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
		print(f"{ctx.author.name}#{ctx.author.discriminator} requested a wordcloud !")
		mentions: List[Member] = ctx.message.mentions
		if len(mentions) == 0:
			mentions.append(ctx.author)
		async with ctx.channel.typing():
			for member in mentions:
				image = make_image.simple_image(self.resolve_words(ctx, self.model.word_cloud(str(member.id), n=2)))
				await ctx.channel.send(
					content=f"**{member.display_name}**'s Word Cloud ({ModelClass.__name__}):",
					file=File(fp=image, filename=f"{member.display_name}_word_cloud.png")
				)
