from typing import List, Tuple
defaultwords = [("No data", 0.70), ("NaN", 0.25), ("nada", 0.025), ("rien", 0.025)]


class Model:
	def add(self, source: str, word: str, weight: float = 1):
		raise NotImplementedError("Abstract add method of Model wasn't implemented.")

	def word_cloud(self, source: str, **kwargs) -> List[Tuple[str, float]]:
		"""
		Returns a word cloud for source
		:param source: the source to generate the word cloud for
		:param kwargs:
		:return: [(word, strength), ...]
		"""
		raise NotImplementedError("Abstract word_cloud method of Model wasn't implemented.")

	def serialize(self) -> str:
		raise NotImplementedError("Abstract serialize method of Model wasn't implemented.")

	@staticmethod
	def parse(text: str) -> "Model":
		raise NotImplementedError("Abstract parse method of Model wasn't implemented.")
