from collections import Counter
from datetime import datetime
from typing import Dict, List, Set
import re
from discord import Guild, Message
import Management.ignored as ignored
from WordCloudModel.model import Model
puncmap = str.maketrans({',': ' ', '.': ' ', '—': ' ', ';': ' ', '’': '\''})
emoreg = re.compile(r'<a?:[^:]+:[0-9]+>')
urlreg = re.compile(r'https?://(?:www.)?([^/]+)')
globreg = re.compile(r'<a?:[^:]+:[0-9]+>|https?://(?:www.)?([^/\s]+)[^\s]+|[\s*]')


def add_to_model(model: Model, words: Dict[str, Counter], msg: Message, n: int = 1):
	userid = str(msg.author.id)
	# we get all the emoji for the string
	emojis: List[str] = emoreg.findall(msg.content)
	for emoji in emojis:
		# add it to the model
		model.add(userid, emoji)
		# add it to the wordlist
		if emoji not in words:
			words[emoji] = Counter()
		words[emoji][userid] += 1

	# split the message content removing the emojis and keeping only domain name in URLs
	tokens: List[str] = list(filter(None, globreg.split(msg.content.lower())))
	# add the content of the message as n-grams to echo
	for word in tokens:
		model.add(userid, word)
		if word not in words:
			words[word] = Counter()
		words[word][userid] += 1
	for i in range(2, n+1):
		for j in range(len(tokens)-i+1):
			model.add(userid, " ".join(tokens[j:j+i]), 1.0/n)


async def load_msgs(guild: Guild, model: Model, words: Dict[str, Counter], limitdate: datetime, maxmsg: int) -> None:
	print(f"Start reading messages for {guild.name}")
	# get the member object representing the bot
	memberself = guild.me
	# get a set of ignored channel ids for this guild
	ignoredchans: Set[int] = set(ignored.ignore_list(guild.id))
	# for every readable channel
	for channel in guild.text_channels:
		# if we can and must read the channel
		if channel.permissions_for(memberself).read_messages and channel.id not in ignoredchans:
			# for every message in the channel after the limit date, from new to old
			async for message in channel.history(limit=maxmsg, after=limitdate, oldest_first=False):
				if not message.author.bot:
					add_to_model(model, words, message)
				# also add the reactions to echo if there's any
				for reaction in message.reactions:
					async for user in reaction.users():
						model.add(str(user.id), str(reaction.emoji))
	print(f"Finished reading messages for {guild.name}")
