import io
from threading import Thread
from typing import Dict
from discord import Guild
import requests
from PIL import Image


class EmojiLoader(Thread):
	def __init__(self, guild: Guild, emo_imgs: Dict, **kwargs):
		Thread.__init__(self, daemon=True, **kwargs)
		self.guild: Guild = guild
		self.emo_imgs: Dict = emo_imgs

	def run(self) -> None:
		print(f"Start loading emojis for {self.guild.name}")
		for emoji in self.guild.emojis:
			if emoji.id not in self.emo_imgs:
				response = requests.get(emoji.url)
				self.emo_imgs[emoji.id] = Image.open(io.BytesIO(response.content))
		print(f"Finished loading emojis for {self.guild.name}")