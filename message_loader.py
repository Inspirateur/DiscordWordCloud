from collections import Counter
from datetime import datetime
from typing import Dict, List, Set
import re
from discord import Guild, Message
import Management.ignored as ignored
from WordCloudModel.model import Model
globreg = re.compile(r'(<a?:[^:]+:[0-9]+>)|https?://(?:www.)?([^/\s]+)[^\s]+|(<..?[0-9]+>)|([\w-]+)|([^\s])')


def add_to_model(model: Model, words: Dict[str, Counter], msg: Message, n: int = 1):
	userid = str(msg.author.id)
	# build the list of tokens without the emojis
	tokens: List[str] = []
	# for every token in the message
	for match in globreg.findall(msg.content):
		# try to look for emoji in the match
		emoji = match[0]
		if emoji:
			# add the emoji to the model
			model.add(userid, emoji)
			# add the emoji to the wordlist
			if emoji not in words:
				words[emoji] = Counter()
			words[emoji][userid] += 1
		else:
			# the match is not an emoji, we look for a token
			token = ''.join(match[1:])
			if token:
				# add the token
				tokens.append(token.lower())

	# add the tokens individually to the model
	for word in tokens:
		model.add(userid, word)
		if word not in words:
			words[word] = Counter()
		words[word][userid] += 1
	# add the tokens as n-grams (n>=2) to the model
	for i in range(2, n+1):
		for j in range(len(tokens)-i+1):
			model.add_n(userid, tuple(tokens[j:j+i]), 1.0/n)


async def load_msgs(guild: Guild, model: Model, n, words: Dict[str, Counter], limitdate: datetime, maxmsg: int) -> None:
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
					add_to_model(model, words, message, n)
				# also add the reactions to echo if there's any
				for reaction in message.reactions:
					async for user in reaction.users():
						emoji = str(reaction.emoji)
						user_id = str(user.id)
						model.add(user_id, emoji)
						if emoji not in words:
							words[emoji] = Counter()
						words[emoji][user_id] += 1
	print(f"Finished reading messages for {guild.name}")
