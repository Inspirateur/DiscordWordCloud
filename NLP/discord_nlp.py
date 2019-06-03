from collections import UserString
from typing import List
import re
discord_emo = r'(<a?:[^:]+:[0-9]+>)'
discord_tag = r'(<..?[0-9]+>)'
url = r'https?://(?:www.)?([^/\s]+)[^\s]+'
# find a proper regex to match all emojis and only emojis
uni_emo = r'([😁-🙏]|[✂-➰]|[🚀-🛀]|[🅰-🉑]|[™-🗿]|[😀-😶]|[🚁-🛅]|[🌍-🕧])'
word = r'([\w-]+)'
nonspace = r'([^\s])'
globreg = re.compile(f'{discord_emo}|{discord_tag}|{url}|{uni_emo}|{word}|{nonspace}')


class Token(UserString):
	"""
	Used when parsing Discord messages, at this stage we just want to know if the token is an emoji or not
	because the emojis will be treated separately
	"""
	def __init__(self, value, is_emoji: bool):
		UserString.__init__(self, value)
		self.is_emoji: bool = is_emoji


def tokenize(msg: str) -> List[Token]:
	tokens = []
	for match in globreg.findall(msg):
		if match[0] != match[3]:
			tokens.append(Token(next(token for token in match if token), True))
		else:
			tokens.append(Token(next(token for token in match if token), False))
	return tokens
	# return [Token(next(token for token in match if token), match[0] != match[3]) for match in globreg.findall(msg)]
