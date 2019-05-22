import io
from typing import List, Tuple, Union
from discord import Emoji
from wordcloud import WordCloud
from WordCloudModel.model import defaultwords


def simple_image(words: List[Tuple[Union[str, Emoji], float]]) -> io.BytesIO:
	"""
	make and save an word cloud image generated with words
	:param words: the words to use
	:return: a virtual image file
	"""
	if len(words) <= 0:
		words = defaultwords
	dictwords = {}
	for (word, value) in words:
		if isinstance(word, Emoji):
			dictwords[f':{word.name}:'] = value
		else:
			dictwords[word] = value
	imgobject = WordCloud(
			"WordCloudImage/Fonts/OpenSansEmoji.otf", scale=2, max_words=None,
			background_color=None, mode="RGBA").fit_words(dictwords).to_image()
	imgbytes = io.BytesIO()
	imgobject.save(imgbytes, format='PNG')
	imgbytes.seek(0)
	return imgbytes
