from typing import List, Tuple, Set
import re
# noinspection PyPackageRequirements
from discord import Guild


def _emoji_pattern():
	import emoji

	EMOJI_UNICODE = emoji.unicode_codes.EMOJI_UNICODE["en"]
	# Sort emojis by length to make sure multi-character emojis are
	# matched first
	emojis = sorted(EMOJI_UNICODE.values(), key=len, reverse=True)
	return '|'.join(re.escape(u) for u in emojis)


re_discord_thing = r"<[^\s]+>"
re_uni_emo = _emoji_pattern()
re_url = r"https?://[^\s]+"
re_word = r"[\w'-]+"
re_token = re.compile(re_discord_thing+"|"+re_uni_emo+"|"+re_url+"|"+re_word)
re_discord_emo = re.compile(r"<a?:\w*:\d*>")
re_discord_tag = re.compile(r"<@&([0-9]+)>|<@!?([0-9]+)>|<#([0-9]+)>")
re_domain = re.compile(r"https?://(?:www.)?([^/\s.]+)[^\s]+")


def smart_lower(txt: str) -> str:
	# lower case only if the first letter is capitalized and not the rest
	if txt[0].isalpha() and txt[1:] == txt[1:].lower():
		return txt.lower()
	return txt


def url_domain(txt: str) -> str:
	match = re_domain.match(txt)
	if match:
		return match[1]
	return txt


def tokenize(msg: str) -> List[str]:
	return map(url_domain, map(smart_lower, filter(None, re_token.findall(msg))))


def get_emojis(msg: str, emojis: Set[str]) -> Set[str]:
	res = set()
	for emoji in re_discord_emo.findall(msg):
		if emoji in emojis:
			res.add(emoji)
	return res


def resolve_tags(guild: Guild, wordcloud: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
	"""
	Make discord tags readable: <@user.id> -> @user.name, <#channel.id> -> #channel.name and so on
	:param guild: the Guild the request was from
	:param wordcloud: the list [(txt, value), ...] to convert
	:return: the same word list with readable tags
	"""
	def repl_tag(match: re.match) -> str:
		if match[1]:
			# it's a role
			role_id = int(match[1])
			role = guild.get_role(role_id)
			return '@'+role.name if role is not None else match[0]
		elif match[2]:
			# it's a member
			member_id = int(match[2])
			member = guild.get_member(member_id)
			return '@'+member.name if member is not None else match[0]
		elif match[3]:
			# it's a channel
			channel_id = int(match[3])
			channel = guild.get_channel(channel_id)
			return '#'+channel.name if channel is not None else match[0]
		return match[0]
	return [(re_discord_tag.sub(repl_tag, txt), val) for txt, val in wordcloud]
