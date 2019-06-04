from typing import List
"""
An attempt to extract a unicode emoji regex from the official Unicode emoji data file (v12.0)
(since I can't find any decent up-to-date regex on the web)
"""


class EmojiRange:
	@staticmethod
	def parse(line: str) -> "EmojiRange":
		r, info = line.split(";")
		rclean = r.strip().split("..")
		start: int = int(rclean[0], 16)
		end: int = start
		if len(rclean) == 2:
			end = int(rclean[1], 16)
		emos = info.split("(", 1)[1].split(")", 1)[0].split("..")
		emo_start: str = emos[0]
		emo_end: str = emo_start
		if len(emos) == 2:
			emo_end = emos[1]
		return EmojiRange(start, end, emo_start, emo_end)

	def __init__(self, start: int, end: int, emo_start: str, emo_end: str):
		self.start: int = start
		self.end: int = end
		self.emo_start: str = emo_start
		self.emo_end: str = emo_end

	def __hash__(self):
		return str(str(self.start)+" "+str(self.end)).__hash__()

	def __eq__(self, other):
		if isinstance(other, EmojiRange):
			return self.start == other.start and self.end == other.end
		else:
			return False

	def __str__(self):
		return f"{'{:5X}'.format(self.start)}..{'{:5X}'.format(self.end)}    " \
			f"{'{:4}'.format(1+self.end-self.start)}    ({self.emo_start}..{self.emo_end})"


def is_relevant(line: str) -> bool:
	return not line.startswith('#') and len(line.strip()) > 0


def combine_range(emoranges: List[EmojiRange]) -> List[EmojiRange]:
	# assemble side by side ranges into one
	filtered: List[EmojiRange] = []
	start = emoranges[0].start
	end = emoranges[0].end
	emo_start = emoranges[0].emo_start
	emo_end = emoranges[0].emo_end
	for emorange in emoranges[1:]:
		if emorange.start - end <= 8:
			end = emorange.end
			emo_end = emorange.emo_end
		else:
			filtered.append(EmojiRange(start, end, emo_start, emo_end))
			start = emorange.start
			end = emorange.end
			emo_start = emorange.emo_start
			emo_end = emorange.emo_end
	return filtered


with open("emoji-data.txt", "r", encoding="utf-8") as emojidata:
	emo_ranges = combine_range(sorted(
		set([EmojiRange.parse(line) for line in emojidata.read().splitlines(keepends=False) if is_relevant(line)]),
		key=lambda x: x.start)
	)


# TODO: remove NAs but don't prevent NAs to be included in a bigger mixed range
with open("emoji-regex.txt", "w", encoding="utf-8") as emojireg:
	emojireg.write("\n".join([str(line) for line in emo_ranges]))
