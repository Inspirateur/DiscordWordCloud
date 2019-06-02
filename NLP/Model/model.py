from typing import List, Tuple
defaultwords = [("No data", 0.70), ("NaN", 0.25), ("nada", 0.025), ("rien", 0.025)]


class Model:
	def add(self, source: str, word: str, weight: float = 1) -> None:
		"""
		Add a word associated with a source to the Model
		:param source: the user associated with word
		:param word: the word to add
		:param weight: the weight of the word
		:return:
		"""
		raise NotImplementedError("Abstract add_n method of Model wasn't implemented.")

	def add_n(self, source: str, words: Tuple[str], weight: float = 1) -> None:
		"""
		Add words associated with a source to the Model
		:param source: the user associated with words
		:param words: a n-gram (could be 1 word)
		:param weight: the weight of the words
		"""
		raise NotImplementedError("Abstract add_n method of Model wasn't implemented.")

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
