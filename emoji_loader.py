import io
from threading import Thread
from typing import Dict
from discord.ext.commands import Bot
import requests
from PIL import Image


class EmojiLoader(Thread):
	def __init__(self, bot: Bot, emo_imgs: Dict, **kwargs):
		Thread.__init__(self, daemon=True, **kwargs)
		self.bot = bot
		self.emo_imgs: Dict = emo_imgs

	def run(self) -> None:
		for guild in self.bot.guilds:
			for emoji in guild.emojis:
				if emoji.id not in self.emo_imgs:
					response = requests.get(emoji.url)
					self.emo_imgs[emoji.id] = Image.open(io.BytesIO(response.content))
