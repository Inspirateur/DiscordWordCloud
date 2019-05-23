import io
from typing import Dict, List, Tuple, Union
from discord import Emoji
import numpy as np
from PIL import Image
from random import randint
import requests
from wordcloud import WordCloud
from WordCloudModel.model import defaultwords
# TODO: for an obscure reason i can't type hint this
# <emoji_id, image>
emo_imgs: Dict = {}


def add_square(mask: np.array, x: int, y: int, size: int):
	for i in range(x, x+size):
		for j in range(y, y+size):
			mask[j][i] = 255


def is_overlapping(boxlist: List[Tuple[int, int, int, int]], x: int, y: int, size: int):
	for (emo_id, ox, oy, osize) in boxlist:
		if not (ox+osize < x or ox > x+size or oy > y+size or oy+osize < y):
			return True
	return False


def simple_image(words: List[Tuple[Union[str, Emoji], float]]) -> io.BytesIO:
	"""
	make and save an word cloud image generated with words
	:param words: the words to use
	:return: a virtual image file
	"""
	if len(words) <= 0:
		words = defaultwords
	# we limit ourselves to the top 200 words
	words = words[:min(len(words), 200)]
	width = 400
	height = 200
	scaling = 2
	mask = np.zeros(shape=(height, width), dtype=int)
	dictwords = {}
	emolist: List[Tuple[Emoji, float]] = []
	total: float = 0.0
	for (word, value) in words:
		if isinstance(word, Emoji):
			if word.id not in emo_imgs:
				response = requests.get(word.url)
				emo_imgs[word.id] = Image.open(io.BytesIO(response.content))
			emolist.append((word, value))
		else:
			dictwords[word] = value
		total += value
	# compute random non-overalapping boxes for the custom emojis
	# boxlist is (emoji_id, x, y, size)
	boxlist: List[Tuple[int, int, int, int]] = []
	for (emoji, value) in emolist:
		size = round(16*height*value/total)
		if size >= 16:
			x = randint(0, width-size)
			y = randint(0, height-size)
			trycount = 0
			while trycount < 10 and is_overlapping(boxlist, x, y, size):
				x = randint(0, width - size)
				y = randint(0, height - size)
				trycount += 1
			add_square(mask, x, y, size)
			boxlist.append((emoji.id, x, y, size))
	# generate the image
	imgobject: Image = WordCloud(
		"WordCloudImage/Fonts/OpenSansEmoji.otf", scale=scaling, max_words=None, mask=mask,
		background_color=None, mode="RGBA"
	).fit_words(dictwords).to_image()
	for (emo_id, x, y, size) in boxlist:
		emo_img: Image = emo_imgs[emo_id].resize((size*scaling, size*scaling))
		imgobject.paste(emo_img, (x*scaling, y*scaling))
	imgbytes = io.BytesIO()
	imgobject.save(imgbytes, format='PNG')
	imgbytes.seek(0)
	return imgbytes
