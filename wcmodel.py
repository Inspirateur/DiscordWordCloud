from typing import Iterable, Hashable, Tuple
defaultwords = [("No data", 0.70), ("NaN", 0.25), ("nada", 0.025), ("rien", 0.025)]


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

	def word_cloud(self, source: Hashable) -> Iterable[Tuple[str, float]]:
		"""
		Returns a word cloud for source
		:param source: the source to generate a word cloud for
		:return: [(text, strength), ...] a summary of the source's messages
		"""
		raise NotImplementedError()
