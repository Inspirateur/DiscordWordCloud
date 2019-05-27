from collections import Counter
from typing import Dict, List, Tuple, Union
import json
from Model.model import Model, defaultwords


class Baseline(Model):
	"""
	A dumb model that just counts the words of everyone,
	and will return the counter without the top 10%
	(which should be filled with common words)
	"""
	def __init__(self):
		# <source, <word, count>>
		self.count: Dict[str, Counter] = {}

	def add(self, source: str, word: str, weight: float = 1) -> None:
		if source not in self.count:
			self.count[source] = Counter()
		self.count[source][word] += weight

	def add_n(self, source: str, words: Tuple[str], weight: float = 1) -> None:
		if source not in self.count:
			self.count[source] = Counter()
		self.count[source][words] += weight

	def word_cloud(self, source: str, **kwargs) -> List[Tuple[str, float]]:
		if source not in self.count:
			return defaultwords
		# get the Top words of source minus the top 10% (which should be filled with common words)
		neartop: List[Tuple[Union[str, Tuple[str]], int]] = self.count[source].most_common()[
															round(len(self.count[source])/10.0):
															]
		# convert the Tuples (n-grams) to strings
		res: List[Tuple[str, float]] = []
		for (ngram, value) in neartop:
			if isinstance(ngram, Tuple):
				res.append((" ".join(ngram), value))
			else:
				res.append((ngram, value))
		return res

	def serialize(self) -> str:
		return json.dumps(self.count)

	@staticmethod
	def parse(text: str) -> "Baseline":
		newbaseline = Baseline()
		newbaseline.count = json.loads(text)
		return newbaseline
