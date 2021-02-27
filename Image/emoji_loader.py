import io
import functools
from os import listdir
from os.path import join
import aiohttp
import discord
from PIL import Image


@functools.cache
def uni_emojis() -> dict:
	"""
	Load all unicode emojis in 72x72 (folder from twemoji).
	Since this is pretty fast we do it in the main thread

	"""
	emo_imgs = {}
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
	return emo_imgs


@functools.cache
async def server_emojis(server: discord.Guild) -> dict:
	"""
	Load all custom server emojis asynchronously
	:param server: the server to load from
	:return: the <emoji_id, Image> dict
	"""
	emo_imgs = {}
	print(f"Start loading emojis for {server.name}")
	async with aiohttp.ClientSession() as session:
		for emoji in server.emojis:
			emoji_str = str(emoji)
			if emoji_str not in emo_imgs:
				async with session.get(str(emoji.url)) as resp:
					if resp.status == 200:
						emo_imgs[emoji_str] = Image.open(io.BytesIO(await resp.read()))
	print(f"Finished loading emojis for {server.name}")
	return emo_imgs
