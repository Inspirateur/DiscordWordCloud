from collections import Counter
from datetime import datetime
from typing import Dict, List, Set
import re
from urllib3.util import parse_url
from discord import Guild, Message
import Management.ignored as ignored
from WordCloudModel.model import Model
puncmap = str.maketrans({',': ' ', '.': ' ', '\n': ' ', '—': ' ', ';': ' ', '’': '\''})
emoreg = re.compile(r'<a?:[^:]+:[0-9]+>')


def add_to_model(model: Model, words: Dict[str, Counter], msg: Message, n: int = 3):
	userid = str(msg.author.id)
	# split the message content with the most basic tokenization
	tokens: List = list(filter(bool, msg.content.split(' ')))
	# separate the emojis from the words
	wordslist: List = []
	for token in tokens:
		if emoreg.match(token):
			# the token is probably an emoji
			model.add(userid, token)
			if token not in words:
				words[token] = Counter()
			words[token][userid] += 1
		elif token.startswith("http"):
			# the token is most likely an url
			url = parse_url(token)
			if len(url.host) > 0:
				# we append the host to the wordlist
				wordslist.append(url.host)
			else:
				# it wasn't an url, we treat the token as a word
				wordslist.append(token.translate(puncmap).lower())
		else:
			# it's probably a word (possibly with punctuation), we treat it and append it
			wordslist.append(token.translate(puncmap).lower())
	# add the content of the message as n-grams to echo
	for word in wordslist:
		model.add(userid, word)
		if word not in words:
			words[word] = Counter()
		words[word][userid] += 1
	for i in range(2, n+1):
		for j in range(len(wordslist)-i+1):
			model.add(userid, " ".join(wordslist[j:j+i]), 1.0/n)


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
