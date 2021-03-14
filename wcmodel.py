from typing import Iterable, Hashable, Tuple


class WCModel:
	"""
	The interface that any WordCloud Model must subclass
	"""
	def train(self, messages: Iterable[Tuple[Hashable, str]]) -> None:
		"""
		Train the model on a series of messages
		:param messages: [(user, msg)]
		"""
		raise NotImplementedError()

	def word_cloud(self, source: Hashable, k=200) -> Iterable[Tuple[str, float]]:
		"""
		Returns a word cloud for source
		:param source: the source to generate a word cloud for
		:param k: limit the output to top k
		:return: [(text, strength), ...] a summary of the source's messages
		"""
		raise NotImplementedError()
