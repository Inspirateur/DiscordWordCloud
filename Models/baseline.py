from collections import defaultdict
from typing import Iterable, Hashable, Tuple
import numpy as np
from preprocessing import tokenize
from wcmodel import WCModel


class WCBaseline(WCModel):
	mat: np.ndarray
	voc: dict
	users: dict

	def __init__(self, alpha=1):
		self.alpha = alpha

	def train(self, messages: Iterable[Tuple[Hashable, str]]) -> None:
		"""
		Train the model on a series of messages
		:param messages: [(user, msg)]
		"""
		g = defaultdict(lambda: defaultdict(int))
		for user, message in messages:
			for token in tokenize(message):
				g[user][token] += 1
		self.voc = {}
		self.users = {}
		for user, tokens in g.items():
			self.users[user] = len(self.users)
			for token in tokens:
				if token not in self.voc:
					self.voc[token] = len(self.voc)
		print(f"mat size: {len(self.users)}x{len(self.voc)} = {len(self.users)*len(self.voc):,}")
		self.mat = np.full((len(self.users), len(self.voc)), fill_value=self.alpha)
		for user, tokens in g.items():
			for token, count in tokens.items():
				self.mat[self.users[user], self.voc[token]] = count
		# normalize user vocabulary
		self.mat = self.mat/self.mat.sum(axis=1)[:, None]

	def word_cloud(self, source: Hashable) -> Iterable[Tuple[str, float]]:
		"""
		Returns a word cloud for source
		:param source: the source to generate a word cloud for
		:return: [(text, strength), ...] a summary of the source's messages
		"""
		if source not in self.users:
			return []
		col = self.mat[self.users[source], :]/self.mat.sum(axis=0)
		return sorted([(token, col[i]) for token, i in self.voc.items()], key=lambda tc: tc[1], reverse=True)
