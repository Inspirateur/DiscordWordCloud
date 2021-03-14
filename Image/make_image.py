import io
from colorsys import hls_to_rgb
from typing import Hashable, Iterable, List, Tuple
from random import randint
from random import Random
import numpy as np
from PIL import Image
from wordcloud import WordCloud
from Image.emoji_loader import EmojiResolver
# proportions of the resulting image
WIDTH = 400
HEIGHT = 200
SCALING = 2


def overlap(boxlist: List[Tuple[int, int, int, int]], x: int, y: int, size: int):
	maxover = 0
	for (emo_id, ox, oy, osize) in boxlist:
		dx = min(x+size, ox+osize) - max(x, ox)
		dy = min(y+size, oy+osize) - max(y, oy)
		if dx > 0 and dy > 0:
			over = dx*dy
			if over > maxover:
				maxover = over
	return maxover


def make_boxlist(emolist: List[Tuple[Hashable, float]]) -> List[Tuple[Hashable, int, int, int]]:
	# FIXME: For now, the emojis can overlap because we're using the "try and see if it works" algorithm
	emoji_scale = 3
	total = sum(value for _, value in emolist)
	# compute random non-overalapping boxes for the custom emojis
	# boxlist is (emoji_id, x, y, size)
	boxlist: List[Tuple[int, int, int, int]] = []
	for (emoji, value) in emolist:
		# compute the size based on the relative strength of the emoji
		size = min(round(HEIGHT/4), round(emoji_scale*HEIGHT*value/total))
		# we only take the emoji if its worth a 16x16 square in our image
		if size >= 16:
			size = max(16, size)
			# randomly place the emoji 10 times and take the least overlapping one
			x, y = min(
				((randint(0, WIDTH-size), randint(0, HEIGHT-size))
				for _ in range(10)),
				key=lambda xy: overlap(boxlist, *xy, size)
			)
			boxlist.append((emoji, x, y, size))
	return boxlist


def color(word: str, random_state: Random, **_):
	if word.startswith("@") or word.startswith("#"):
		return 114, 137, 218
	return tuple(int(v*255) for v in hls_to_rgb(random_state.random(), .7, .9))


async def wc_image(wc: Iterable[Tuple[str, float]], emoji_imgs: EmojiResolver) -> io.BytesIO:
	"""
	make and save an word cloud image generated with words and emojis
	:param wc: the word cloud data
	:param emoji_imgs: <emoji: str, Image> mapping
	:return: a virtual image file
	"""
	# split the wc into words and emojis
	str_wc = []
	emo_wc = []
	for token, value in wc:
		if await emoji_imgs.contains(token):
			emo_wc.append((token, value))
		else:
			str_wc.append((token, value))
	# we create the mask image
	mask = np.zeros(shape=(HEIGHT, WIDTH), dtype=int)

	# compute the boxlist representing the space taken by emoji pics
	boxlist = make_boxlist(emo_wc)
	# apply the alpha of every emoji on the mask if it exists, else mask out the box
	for (emo_id, x, y, size) in boxlist:
		emo_img = emoji_imgs[emo_id]
		if emo_img.mode in ("RGBA", "LA") or (emo_img.mode == "P" and "transparency" in emo_img.info):
			emo_img = emo_img.convert("RGBA").resize((size, size))
			mask[y:y + size, x:x + size] = np.asarray(emo_img.split()[-1]).copy()
		else:
			mask[y:y + size, x:x + size] = 255

	# generate the image
	imgobject: Image = WordCloud(
		"Image/Fonts/whitneymedium.otf", WIDTH, HEIGHT, scale=SCALING, max_words=None, mask=mask,
		background_color=None, mode="RGBA", color_func=color
	).fit_words(dict(str_wc)).to_image()

	# paste the emojis from boxlist to the image
	for (emo_id, x, y, size) in boxlist:
		# get the scaled emoji picture
		emo_img: Image = emoji_imgs[emo_id].resize((size*SCALING, size*SCALING)).convert("RGBA")
		# paste it in the pre-defined box
		imgobject.alpha_composite(emo_img, (x*SCALING, y*SCALING))

	# get and return the image bytes
	imgbytes = io.BytesIO()
	imgobject.save(imgbytes, format='PNG')
	imgbytes.seek(0)
	return imgbytes
