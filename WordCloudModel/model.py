from typing import List, Tuple
defaultwords = [("No data", 0.70), ("NaN", 0.25), ("nada", 0.025), ("rien", 0.025)]


class Model:
	def __contains__(self, item) -> bool:
		raise NotImplementedError("Abstract __contains__ method of Model wasn't implemented.")

	def add(self, source: str, word: str, weight: float = 1):
		raise NotImplementedError("Abstract add method of Model wasn't implemented.")

	def word_cloud(self, source: str, **kwargs) -> List[Tuple[str, float]]:
		raise NotImplementedError("Abstract word_cloud method of Model wasn't implemented.")

	def word_use(self, word: str) -> List[Tuple[str, float]]:
		raise NotImplementedError("Abstract word_use method of Model wasn't implemented")

	def serialize(self) -> str:
		raise NotImplementedError("Abstract serialize method of Model wasn't implemented.")

	@staticmethod
	def parse(text: str) -> "Model":
		raise NotImplementedError("Abstract parse method of Model wasn't implemented.")
