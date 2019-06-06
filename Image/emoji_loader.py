import io
from os import listdir
from os.path import join
from typing import Dict
import aiohttp
from discord import Guild
from PIL import Image


def load_uni_emojis(emo_imgs: Dict) -> None:
	"""
	Load all unicode emojis in 72x72 (folder from twemoji).
	Since this is pretty fast we do it in the main thread

	"""
	print(f"Start loading unicode emojis")
	twemoji_path = join("Image", "72x72")
	emofiles = listdir(twemoji_path)
	# for every emoji file in twemoji
	for emofile in emofiles:
		filename, _ = emofile.split(".")
		# get the emoji codepoint(s)
		emocodes = filename.split("-")
		# for every emoji codepoint
		for emocode in emocodes:
			# load the image using the unicode char as key
			emo_imgs[chr(int(emocode, 16))] = Image.open(join(twemoji_path, emofile))
	print(f"Finished loading unicode emojis")


async def load_guild_emojis(guild: Guild, emo_imgs: Dict) -> None:
	"""
	Load all custom guild emojis asynchronously
	:param guild: the guild to load from
	:param emo_imgs: the <emoji_id, Image> dict
	"""
	print(f"Start loading emojis for {guild.name}")
	async with aiohttp.ClientSession() as session:
		for emoji in guild.emojis:
			if emoji.id not in emo_imgs:
				async with session.get(str(emoji.url)) as resp:
					if resp.status == 200:
						emo_imgs[str(emoji.id)] = Image.open(io.BytesIO(await resp.read()))
	print(f"Finished loading emojis for {guild.name}")
