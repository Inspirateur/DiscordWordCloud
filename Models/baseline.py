from collections import defaultdict
from typing import Iterable, Hashable, Tuple
import numpy as np
from preprocessing import tokenize
from wcmodel import WCModel


class WCBaseline(WCModel):
	mat: np.ndarray
	# [tokens]
	voc: list
	# <user, index>
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
		# at first voc is <token, index>
		self.voc: dict = {}
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
		# turn voc into the list of tokens, useful in word_cloud
		self.voc = list(self.voc.keys())
		# normalize user vocabulary
		self.mat = self.mat/self.mat.sum(axis=1)[:, None]

	def word_cloud(self, source: Hashable, k=200) -> Iterable[Tuple[str, float]]:
		"""
		Returns a word cloud for source
		:param source: the source to generate a word cloud for
		:param k: limit the output to top k
		:return: [(text, strength), ...] a summary of the source's messages
		"""
		if source not in self.users:
			return []
		score = self.mat[self.users[source], :]/self.mat.sum(axis=0)
		ind = np.argpartition(score, -k)[-k:]
		return [(self.voc[i], score[i]) for i in ind]
