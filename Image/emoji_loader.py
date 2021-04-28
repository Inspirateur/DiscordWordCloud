from typing import Optional
import io
from os import listdir
from os.path import join
import sys
import aiohttp
# noinspection PyPackageRequirements
import discord
from PIL import Image
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio


def uni_emojis() -> dict:
	"""
	Load all unicode emojis in 72x72 (folder from twemoji).
	Since this is pretty fast we do it in the main thread
	"""
	emo_imgs = {}
	twemoji_path = join("Image", "72x72")
	emofiles = listdir(twemoji_path)
	# for every emoji file in twemoji
	for emofile in tqdm(emofiles, desc="Unicode Emojis", ncols=140, file=sys.stdout):
		filename, _ = emofile.split(".")
		# get the emoji codepoint(s)
		emocodes = filename.split("-")
		# for every emoji codepoint
		for emocode in emocodes:
			# load the image using the unicode char as key
			key = chr(int(emocode, 16))
			emo_imgs[key] = Image.open(join(twemoji_path, emofile))
			# load the image in memory now so the file can be closed
			# see https://pillow.readthedocs.io/en/stable/reference/open_files.html#file-handling
			emo_imgs[key].load()
	return emo_imgs


async def external_emoji(emo_id: int) -> Optional[Image.Image]:
	# NOTE: this is bad code, but it's a pain to get that with the library
	emoji_url = f"https://cdn.discordapp.com/emojis/{emo_id}.png?v=1"
	async with aiohttp.ClientSession() as session:
		async with session.get(emoji_url) as resp:
			if resp.status == 200:
				return Image.open(io.BytesIO(await resp.read()))
	return None


async def server_emojis(server: discord.Guild) -> dict:
	"""
	Load all custom server emojis asynchronously
	:param server: the server to load from
	:return: the <emoji_id, Image> dict
	"""
	emo_imgs = {}
	async with aiohttp.ClientSession() as session:
		for emoji in tqdm_asyncio(server.emojis, desc=f"Emojis {server.name}", ncols=140, file=sys.stdout):
			emoji_str = str(emoji)
			if emoji_str not in emo_imgs:
				async with session.get(str(emoji.url)) as resp:
					if resp.status == 200:
						emo_imgs[emoji_str] = Image.open(io.BytesIO(await resp.read()))
	return emo_imgs


class EmojiResolver:
	def __init__(self, client: discord.Client):
		self.client = client
		self._mapping = uni_emojis()

	async def load_server_emojis(self, server=None):
		if server is not None:
			self._mapping.update(await server_emojis(server))
		else:
			for server in self.client.guilds:
				self._mapping.update(await server_emojis(server))

	async def contains(self, emoji: str):
		if emoji in self._mapping:
			return True
		# try to extract an id and load it as an external discord emoji
		try:
			emo_id = int(emoji.split(":")[-1][:-1])
			img = await external_emoji(emo_id)
			if img is not None:
				self._mapping[emoji] = img
			return img is not None
		except ValueError:
			return False

	def __getitem__(self, emoji: str):
		return self._mapping[emoji]
