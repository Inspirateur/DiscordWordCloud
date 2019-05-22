from collections import Counter
from typing import Dict, List, Tuple
import json
from WordCloudModel.model import Model, defaultwords


class Baseline(Model):
	"""
	A dumb model that just counts the words of everyone,
	and will return the counter without the top 10%
	(which should be filled with common words)
	"""
	def __init__(self):
		# <source, <word, count>>
		self.count: Dict[str, Counter] = {}

	def __contains__(self, item):
		return item in self.count

	def add(self, source: str, word: str, weight: float = 1):
		if source not in self.count:
			self.count[source] = Counter()
		self.count[source][word] += weight

	def word_cloud(self, source: str, **kwargs) -> List[Tuple[str, float]]:
		if source not in self.count:
			return defaultwords
		return self.count[source].most_common()[round(len(self.count[source])/10.0):]

	def word_use(self, word: str) -> List[Tuple[str, float]]:
		res = []
		for user in self.count:
			if word in user:
				res.append((user, self.count[user][word]))
		return sorted(res, key=lambda x: x[1], reverse=True)

	def word_use_count(self, word: str) -> int:
		total = 0
		for user in self.count:
			total += self.count[user][word]
		return total

	def serialize(self) -> str:
		return json.dumps(self.count)

	@staticmethod
	def parse(text: str) -> "Baseline":
		newbaseline = Baseline()
		newbaseline.count = json.loads(text)
		return newbaseline
