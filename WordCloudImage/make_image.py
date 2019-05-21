from typing import List, Tuple
from wordcloud import WordCloud
from WordCloudModel.model import defaultwords


def simple_image(words: List[Tuple[str, float]], userid: str) -> str:
	"""
	make and save an word cloud image generated with words
	:param words: the words to use
	:param userid: the unique ID we'll use to make a unique filename
	:return: the path to the saved image
	"""
	filepath = f"WordCloudImage/Images/{userid}.png"
	if len(words) <= 1:
		words = defaultwords
	WordCloud(
		"WordCloudImage/Fonts/OpenSansEmoji.otf", scale=2, max_words=None,
		background_color=None, mode="RGBA").fit_words(dict(words)).to_file(filepath)
	return filepath
