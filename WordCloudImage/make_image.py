import io
from typing import Dict, List, Tuple, Union
from discord import Emoji
import numpy as np
from PIL import Image
import requests
from wordcloud import WordCloud
from WordCloudModel.model import defaultwords
emo_imgs: Dict = {}


def simple_image(words: List[Tuple[Union[str, Emoji], float]]) -> io.BytesIO:
	"""
	make and save an word cloud image generated with words
	:param words: the words to use
	:return: a virtual image file
	"""
	if len(words) <= 0:
		words = defaultwords
	mask = np.zeros(shape=(200, 400), dtype=int)
	dictwords = {}
	for (word, value) in words:
		if isinstance(word, Emoji):
			if word.id not in emo_imgs:
				response = requests.get(word.url)
				emo_imgs[word.id] = Image.open(io.BytesIO(response.content))
			dictwords[f':{word.name}:'] = value
		else:
			dictwords[word] = value
	imgobject = WordCloud(
		"WordCloudImage/Fonts/OpenSansEmoji.otf", scale=2, max_words=None, mask=mask,
		contour_width=4, background_color=None, mode="RGB"
	).fit_words(dictwords).to_image()
	imgbytes = io.BytesIO()
	imgobject.save(imgbytes, format='PNG')
	imgbytes.seek(0)
	return imgbytes
