from typing import Iterable, Hashable, Tuple
from preprocessing import tokenize
from wcmodel import WCModel


class WCBaseline(WCModel):
	# TODO: this, with either csr+csc or a dense matrix of tokens by users
	#  (normalize by col and row and use a topk to get wc)
	def __init__(self):
		...

	def train(self, messages: Iterable[Tuple[Hashable, str]]) -> None:
		"""
		Train the model on a series of messages
		:param messages: [(user, msg)]
		"""
		...

	def word_cloud(self, source: Hashable) -> Iterable[Tuple[str, float]]:
		"""
		Returns a word cloud for source
		:param source: the source to generate a word cloud for
		:return: [(text, strength), ...] a summary of the source's messages
		"""
		...
