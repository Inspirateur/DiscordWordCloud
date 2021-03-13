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


def is_overlapping(boxlist: List[Tuple[int, int, int, int]], x: int, y: int, size: int):
	for (emo_id, ox, oy, osize) in boxlist:
		if not (ox+osize < x or ox > x+size or oy > y+size or oy+osize < y):
			return True
	return len(boxlist) > 0


def make_boxlist(emolist: List[Tuple[Hashable, float]]) -> List[Tuple[Hashable, int, int, int]]:
	# FIXME: For now, the emojis can overlap because we're using the "try and see if it works" algorithm
	emoji_scale = 8
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
			# tries to generate a random non-overlapping box with this size (10 tries max)
			for tries in range(10):
				x = randint(0, WIDTH-size)
				y = randint(0, HEIGHT-size)
				if not is_overlapping(boxlist, x, y, size):
					boxlist.append((emoji, x, y, size))
					break
			else:
				# we couldn't generate a non-overlapping box in 10 tries, we generate one without checking
				x = randint(0, WIDTH-size)
				y = randint(0, HEIGHT-size)
				boxlist.append((emoji, x, y, size))
	return boxlist


def color(word: str, font_size, position, orientation, font_path, random_state: Random):
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
	# apply every box in boxlist to the mask
	for (emo_id, x, y, size) in boxlist:
		mask[y:y + size, x:x + size] = 255

	# generate the image
	imgobject: Image = WordCloud(
		"Image/Fonts/whitneymedium.otf", WIDTH, HEIGHT, scale=SCALING, max_words=None, mask=mask,
		background_color=None, mode="RGBA", color_func=color
	).fit_words(dict(str_wc[:200])).to_image()

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
