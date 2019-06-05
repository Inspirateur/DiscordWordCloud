import io
from typing import Dict, List, Tuple, Union
from discord import Emoji
import numpy as np
from PIL import Image
from random import randint
from urllib.request import Request, urlopen
from wordcloud import WordCloud
from NLP.Models.model import defaultwords
# FIXME: for an obscure reason i can't type hint this
# <emoji_id, image>
emo_imgs: Dict = {}
# proportions of the resulting image
width = 400
height = 200
scaling = 2


def is_overlapping(boxlist: List[Tuple[int, int, int, int]], x: int, y: int, size: int):
	for (emo_id, ox, oy, osize) in boxlist:
		if not (ox+osize < x or ox > x+size or oy > y+size or oy+osize < y):
			return True
	return len(boxlist) > 0


def simple_image(words: List[Tuple[Union[str, Emoji], float]]) -> io.BytesIO:
	# TODO: the emojis and the words have now been separated, reflect the changes here
	"""
	make and save an word cloud image generated with words
	:param words: the words to use
	:return: a virtual image file
	"""
	if len(words) <= 0:
		words = defaultwords
	# we limit ourselves to the top 200 words
	words = words[:200]
	mask = np.zeros(shape=(height, width), dtype=int)
	dictwords = {}
	emolist: List[Tuple[Emoji, float]] = []
	total: float = 0.0
	for (word, value) in words:
		if isinstance(word, Emoji):
			if word.id not in emo_imgs:
				emo_imgs[word.id] = Image.open(io.BytesIO(urlopen(
					Request(str(word.url), headers={'User-Agent': 'Mozilla/5.0'})
				).read()))
			emolist.append((word, value))
		else:
			dictwords[word] = value
		total += value
	# compute random non-overalapping boxes for the custom emojis
	# boxlist is (emoji_id, x, y, size)
	boxlist: List[Tuple[int, int, int, int]] = []
	for (emoji, value) in emolist:
		# compute the size based on the relative strength of the emoji
		size = max(16, min(round(height/2), round(4*height*value/total)))
		# tries to generate a random non-overlapping box with this size (10 tries max)
		for tries in range(10):
			x = randint(0, width-size)
			y = randint(0, height-size)
			if not is_overlapping(boxlist, x, y, size):
				boxlist.append((emoji.id, x, y, size))
				break
		else:
			# we couldn't generate a non-overlapping box in 10 tries, we generate one without checking
			x = randint(0, width-size)
			y = randint(0, height-size)
			boxlist.append((emoji.id, x, y, size))

	# apply every box in boxlist to the mask
	for (emo_id, x, y, size) in boxlist:
		mask[y:y + size, x:x + size] = 255

	# generate the image
	imgobject: Image = WordCloud(
		"Image/Fonts/OpenSansEmoji.otf", scale=scaling, max_words=None, mask=mask,
		background_color=None, mode="RGBA"
	).fit_words(dictwords).to_image()

	# paste the emojis from boxlist to the image
	for (emo_id, x, y, size) in boxlist:
		# get the scaled emoji picture
		emo_img: Image = emo_imgs[emo_id].resize((size*scaling, size*scaling))
		# paste it in the pre-defined box
		imgobject.paste(emo_img, (x*scaling, y*scaling))

	# get and return the image bytes
	imgbytes = io.BytesIO()
	imgobject.save(imgbytes, format='PNG')
	imgbytes.seek(0)
	return imgbytes
