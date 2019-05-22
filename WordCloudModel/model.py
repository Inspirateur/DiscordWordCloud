from typing import List, Tuple
defaultwords = [("No data", 0.70), ("NaN", 0.25), ("nada", 0.025), ("rien", 0.025)]


class Model:
	def __contains__(self, item) -> bool:
		raise NotImplementedError("Abstract __contains__ method of Model wasn't implemented.")

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

	def word_use(self, word: str) -> List[Tuple[str, float]]:
		"""
		Returns the list of user with how much they used word, sorted by descending order
		:param word: the word to inspect
		:return: [(user, use of word), ...]
		"""
		raise NotImplementedError("Abstract word_use method of Model wasn't implemented")

	def word_use_count(self, word: str) -> int:
		"""
		Returns how much word was used
		:param word: the word to inspect
		:return: how much it was used
		"""
		raise NotImplementedError("Abstract word_use_count method of Model wasn't implemented")

	def serialize(self) -> str:
		raise NotImplementedError("Abstract serialize method of Model wasn't implemented.")

	@staticmethod
	def parse(text: str) -> "Model":
		raise NotImplementedError("Abstract parse method of Model wasn't implemented.")
