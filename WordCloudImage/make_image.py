import io
from typing import List, Tuple
from wordcloud import WordCloud
from WordCloudModel.model import defaultwords


def virtual_image(words: List[Tuple[str, float]]) -> io.BytesIO:
	"""
	make and save an word cloud image generated with words
	:param words: the words to use
	:return: a virtual image file
	"""
	if len(words) <= 0:
		words = defaultwords
	imgobject = WordCloud(
			"WordCloudImage/Fonts/OpenSansEmoji.otf", scale=2, max_words=None,
			background_color=None, mode="RGBA").fit_words(dict(words)).to_image()
	imgbytes = io.BytesIO()
	imgobject.save(imgbytes, format='PNG')
	imgbytes.seek(0)
	return imgbytes
