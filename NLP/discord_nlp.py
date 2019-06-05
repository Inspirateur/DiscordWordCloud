from collections import UserString
from typing import List, Iterator, Tuple, Union
import re


class Token(UserString):
	"""
	Used when parsing Discord messages, at this stage we just want to know if the token is an emoji or not
	because the emojis will be treated separately
	"""
	def __init__(self, value, is_emoji: bool):
		# if it's not an emoji and a title we lower-case the value
		UserString.__init__(self, value.lower() if not is_emoji and value.istitle() else value)
		self.is_emoji: bool = is_emoji


discord_emo = r'(<a?:[^:]+:[0-9]+>)'
discord_tag = r'(<..?[0-9]+>)'
url = r'https?://(?:www.)?([^/\s]+)[^\s]+'
uni_emo = r'(\U0001F3F4\U000E0067\U000E0062(?:\U000E0077\U000E006C\U000E0073|\U000E0073\U000E0063\U000E0074|\U000E0065\U000E006E\U000E0067)\U000E007F|(?:\U0001F9D1\U0001F3FB\u200D\U0001F91D\u200D\U0001F9D1|\U0001F469\U0001F3FC\u200D\U0001F91D\u200D\U0001F469)\U0001F3FB|\U0001F468(?:\U0001F3FC\u200D(?:\U0001F91D\u200D\U0001F468\U0001F3FB|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FF\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FB-\U0001F3FE]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FE\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FB-\U0001F3FD]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FD\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FB\U0001F3FC]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\u200D(?:\u2764\uFE0F\u200D(?:\U0001F48B\u200D)?\U0001F468|[\U0001F468\U0001F469]\u200D(?:\U0001F466\u200D\U0001F466|\U0001F467\u200D[\U0001F466\U0001F467])|\U0001F466\u200D\U0001F466|\U0001F467\u200D[\U0001F466\U0001F467]|[\U0001F468\U0001F469]\u200D[\U0001F466\U0001F467]|[\u2695\u2696\u2708]\uFE0F|[\U0001F466\U0001F467]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|(?:\U0001F3FB\u200D[\u2695\u2696\u2708]|\U0001F3FF\u200D[\u2695\u2696\u2708]|\U0001F3FE\u200D[\u2695\u2696\u2708]|\U0001F3FD\u200D[\u2695\u2696\u2708]|\U0001F3FC\u200D[\u2695\u2696\u2708])\uFE0F|\U0001F3FB\u200D[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]|[\U0001F3FB-\U0001F3FF])|\U0001F9D1(?:\U0001F3FF\u200D\U0001F91D\u200D\U0001F9D1[\U0001F3FB-\U0001F3FF]|\u200D\U0001F91D\u200D\U0001F9D1)|\U0001F469(?:\U0001F3FE\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FB-\U0001F3FD\U0001F3FF]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FD\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FB\U0001F3FC\U0001F3FE\U0001F3FF]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FC\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FB\U0001F3FD-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FB\u200D(?:\U0001F91D\u200D\U0001F468[\U0001F3FC-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\u200D(?:\u2764\uFE0F\u200D(?:\U0001F48B\u200D[\U0001F468\U0001F469]|[\U0001F468\U0001F469])|[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FF\u200D[\U0001F33E\U0001F373\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|(?:\U0001F9D1\U0001F3FE\u200D\U0001F91D\u200D\U0001F9D1|\U0001F469\U0001F3FF\u200D\U0001F91D\u200D[\U0001F468\U0001F469])[\U0001F3FB-\U0001F3FE]|(?:\U0001F9D1\U0001F3FD\u200D\U0001F91D\u200D\U0001F9D1|\U0001F469\U0001F3FE\u200D\U0001F91D\u200D\U0001F469)[\U0001F3FB-\U0001F3FD]|(?:\U0001F9D1\U0001F3FC\u200D\U0001F91D\u200D\U0001F9D1|\U0001F469\U0001F3FD\u200D\U0001F91D\u200D\U0001F469)[\U0001F3FB\U0001F3FC]|\U0001F469\u200D\U0001F469\u200D(?:\U0001F466\u200D\U0001F466|\U0001F467\u200D[\U0001F466\U0001F467])|\U0001F469\u200D\U0001F466\u200D\U0001F466|\U0001F469\u200D\U0001F469\u200D[\U0001F466\U0001F467]|(?:\U0001F441\uFE0F\u200D\U0001F5E8|\U0001F469(?:\U0001F3FF\u200D[\u2695\u2696\u2708]|\U0001F3FE\u200D[\u2695\u2696\u2708]|\U0001F3FD\u200D[\u2695\u2696\u2708]|\U0001F3FC\u200D[\u2695\u2696\u2708]|\U0001F3FB\u200D[\u2695\u2696\u2708]|\u200D[\u2695\u2696\u2708])|[\U0001F3C3\U0001F3C4\U0001F3CA\U0001F46E\U0001F471\U0001F473\U0001F477\U0001F481\U0001F482\U0001F486\U0001F487\U0001F645-\U0001F647\U0001F64B\U0001F64D\U0001F64E\U0001F6A3\U0001F6B4-\U0001F6B6\U0001F926\U0001F937-\U0001F939\U0001F93D\U0001F93E\U0001F9B8\U0001F9B9\U0001F9CD-\U0001F9CF\U0001F9D6-\U0001F9DD][\U0001F3FB-\U0001F3FF]\u200D[\u2640\u2642]|[\u26F9\U0001F3CB\U0001F3CC\U0001F575](?:\uFE0F\u200D[\u2640\u2642]|[\U0001F3FB-\U0001F3FF]\u200D[\u2640\u2642])|\U0001F3F4\u200D\u2620|[\U0001F3C3\U0001F3C4\U0001F3CA\U0001F46E\U0001F46F\U0001F471\U0001F473\U0001F477\U0001F481\U0001F482\U0001F486\U0001F487\U0001F645-\U0001F647\U0001F64B\U0001F64D\U0001F64E\U0001F6A3\U0001F6B4-\U0001F6B6\U0001F926\U0001F937-\U0001F939\U0001F93C-\U0001F93E\U0001F9B8\U0001F9B9\U0001F9CD-\U0001F9CF\U0001F9D6-\U0001F9DF]\u200D[\u2640\u2642])\uFE0F|\U0001F469\u200D\U0001F467\u200D[\U0001F466\U0001F467]|\U0001F3F3\uFE0F\u200D\U0001F308|\U0001F469\u200D\U0001F467|\U0001F469\u200D\U0001F466|\U0001F415\u200D\U0001F9BA|\U0001F1FD\U0001F1F0|\U0001F1F6\U0001F1E6|\U0001F1F4\U0001F1F2|\U0001F9D1[\U0001F3FB-\U0001F3FF]|\U0001F469[\U0001F3FB-\U0001F3FF]|\U0001F1FF[\U0001F1E6\U0001F1F2\U0001F1FC]|\U0001F1FE[\U0001F1EA\U0001F1F9]|\U0001F1FC[\U0001F1EB\U0001F1F8]|\U0001F1FB[\U0001F1E6\U0001F1E8\U0001F1EA\U0001F1EC\U0001F1EE\U0001F1F3\U0001F1FA]|\U0001F1FA[\U0001F1E6\U0001F1EC\U0001F1F2\U0001F1F3\U0001F1F8\U0001F1FE\U0001F1FF]|\U0001F1F9[\U0001F1E6\U0001F1E8\U0001F1E9\U0001F1EB-\U0001F1ED\U0001F1EF-\U0001F1F4\U0001F1F7\U0001F1F9\U0001F1FB\U0001F1FC\U0001F1FF]|\U0001F1F8[\U0001F1E6-\U0001F1EA\U0001F1EC-\U0001F1F4\U0001F1F7-\U0001F1F9\U0001F1FB\U0001F1FD-\U0001F1FF]|\U0001F1F7[\U0001F1EA\U0001F1F4\U0001F1F8\U0001F1FA\U0001F1FC]|\U0001F1F5[\U0001F1E6\U0001F1EA-\U0001F1ED\U0001F1F0-\U0001F1F3\U0001F1F7-\U0001F1F9\U0001F1FC\U0001F1FE]|\U0001F1F3[\U0001F1E6\U0001F1E8\U0001F1EA-\U0001F1EC\U0001F1EE\U0001F1F1\U0001F1F4\U0001F1F5\U0001F1F7\U0001F1FA\U0001F1FF]|\U0001F1F2[\U0001F1E6\U0001F1E8-\U0001F1ED\U0001F1F0-\U0001F1FF]|\U0001F1F1[\U0001F1E6-\U0001F1E8\U0001F1EE\U0001F1F0\U0001F1F7-\U0001F1FB\U0001F1FE]|\U0001F1F0[\U0001F1EA\U0001F1EC-\U0001F1EE\U0001F1F2\U0001F1F3\U0001F1F5\U0001F1F7\U0001F1FC\U0001F1FE\U0001F1FF]|\U0001F1EF[\U0001F1EA\U0001F1F2\U0001F1F4\U0001F1F5]|\U0001F1EE[\U0001F1E8-\U0001F1EA\U0001F1F1-\U0001F1F4\U0001F1F6-\U0001F1F9]|\U0001F1ED[\U0001F1F0\U0001F1F2\U0001F1F3\U0001F1F7\U0001F1F9\U0001F1FA]|\U0001F1EC[\U0001F1E6\U0001F1E7\U0001F1E9-\U0001F1EE\U0001F1F1-\U0001F1F3\U0001F1F5-\U0001F1FA\U0001F1FC\U0001F1FE]|\U0001F1EB[\U0001F1EE-\U0001F1F0\U0001F1F2\U0001F1F4\U0001F1F7]|\U0001F1EA[\U0001F1E6\U0001F1E8\U0001F1EA\U0001F1EC\U0001F1ED\U0001F1F7-\U0001F1FA]|\U0001F1E9[\U0001F1EA\U0001F1EC\U0001F1EF\U0001F1F0\U0001F1F2\U0001F1F4\U0001F1FF]|\U0001F1E8[\U0001F1E6\U0001F1E8\U0001F1E9\U0001F1EB-\U0001F1EE\U0001F1F0-\U0001F1F5\U0001F1F7\U0001F1FA-\U0001F1FF]|\U0001F1E7[\U0001F1E6\U0001F1E7\U0001F1E9-\U0001F1EF\U0001F1F1-\U0001F1F4\U0001F1F6-\U0001F1F9\U0001F1FB\U0001F1FC\U0001F1FE\U0001F1FF]|\U0001F1E6[\U0001F1E8-\U0001F1EC\U0001F1EE\U0001F1F1\U0001F1F2\U0001F1F4\U0001F1F6-\U0001F1FA\U0001F1FC\U0001F1FD\U0001F1FF]|[#\*0-9]\uFE0F\u20E3|[\U0001F3C3\U0001F3C4\U0001F3CA\U0001F46E\U0001F471\U0001F473\U0001F477\U0001F481\U0001F482\U0001F486\U0001F487\U0001F645-\U0001F647\U0001F64B\U0001F64D\U0001F64E\U0001F6A3\U0001F6B4-\U0001F6B6\U0001F926\U0001F937-\U0001F939\U0001F93D\U0001F93E\U0001F9B8\U0001F9B9\U0001F9CD-\U0001F9CF\U0001F9D6-\U0001F9DD][\U0001F3FB-\U0001F3FF]|[\u26F9\U0001F3CB\U0001F3CC\U0001F575][\U0001F3FB-\U0001F3FF]|[\u261D\u270A-\u270D\U0001F385\U0001F3C2\U0001F3C7\U0001F442\U0001F443\U0001F446-\U0001F450\U0001F466\U0001F467\U0001F46B-\U0001F46D\U0001F470\U0001F472\U0001F474-\U0001F476\U0001F478\U0001F47C\U0001F483\U0001F485\U0001F4AA\U0001F574\U0001F57A\U0001F590\U0001F595\U0001F596\U0001F64C\U0001F64F\U0001F6C0\U0001F6CC\U0001F90F\U0001F918-\U0001F91C\U0001F91E\U0001F91F\U0001F930-\U0001F936\U0001F9B5\U0001F9B6\U0001F9BB\U0001F9D2-\U0001F9D5][\U0001F3FB-\U0001F3FF]|[\u231A\u231B\u23E9-\u23EC\u23F0\u23F3\u25FD\u25FE\u2614\u2615\u2648-\u2653\u267F\u2693\u26A1\u26AA\u26AB\u26BD\u26BE\u26C4\u26C5\u26CE\u26D4\u26EA\u26F2\u26F3\u26F5\u26FA\u26FD\u2705\u270A\u270B\u2728\u274C\u274E\u2753-\u2755\u2757\u2795-\u2797\u27B0\u27BF\u2B1B\u2B1C\u2B50\u2B55\U0001F004\U0001F0CF\U0001F18E\U0001F191-\U0001F19A\U0001F1E6-\U0001F1FF\U0001F201\U0001F21A\U0001F22F\U0001F232-\U0001F236\U0001F238-\U0001F23A\U0001F250\U0001F251\U0001F300-\U0001F320\U0001F32D-\U0001F335\U0001F337-\U0001F37C\U0001F37E-\U0001F393\U0001F3A0-\U0001F3CA\U0001F3CF-\U0001F3D3\U0001F3E0-\U0001F3F0\U0001F3F4\U0001F3F8-\U0001F43E\U0001F440\U0001F442-\U0001F4FC\U0001F4FF-\U0001F53D\U0001F54B-\U0001F54E\U0001F550-\U0001F567\U0001F57A\U0001F595\U0001F596\U0001F5A4\U0001F5FB-\U0001F64F\U0001F680-\U0001F6C5\U0001F6CC\U0001F6D0-\U0001F6D2\U0001F6D5\U0001F6EB\U0001F6EC\U0001F6F4-\U0001F6FA\U0001F7E0-\U0001F7EB\U0001F90D-\U0001F93A\U0001F93C-\U0001F945\U0001F947-\U0001F971\U0001F973-\U0001F976\U0001F97A-\U0001F9A2\U0001F9A5-\U0001F9AA\U0001F9AE-\U0001F9CA\U0001F9CD-\U0001F9FF\U0001FA70-\U0001FA73\U0001FA78-\U0001FA7A\U0001FA80-\U0001FA82\U0001FA90-\U0001FA95]|[#\*0-9\xA9\xAE\u203C\u2049\u2122\u2139\u2194-\u2199\u21A9\u21AA\u231A\u231B\u2328\u23CF\u23E9-\u23F3\u23F8-\u23FA\u24C2\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE\u2600-\u2604\u260E\u2611\u2614\u2615\u2618\u261D\u2620\u2622\u2623\u2626\u262A\u262E\u262F\u2638-\u263A\u2640\u2642\u2648-\u2653\u265F\u2660\u2663\u2665\u2666\u2668\u267B\u267E\u267F\u2692-\u2697\u2699\u269B\u269C\u26A0\u26A1\u26AA\u26AB\u26B0\u26B1\u26BD\u26BE\u26C4\u26C5\u26C8\u26CE\u26CF\u26D1\u26D3\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934\u2935\u2B05-\u2B07\u2B1B\u2B1C\u2B50\u2B55\u3030\u303D\u3297\u3299\U0001F004\U0001F0CF\U0001F170\U0001F171\U0001F17E\U0001F17F\U0001F18E\U0001F191-\U0001F19A\U0001F1E6-\U0001F1FF\U0001F201\U0001F202\U0001F21A\U0001F22F\U0001F232-\U0001F23A\U0001F250\U0001F251\U0001F300-\U0001F321\U0001F324-\U0001F393\U0001F396\U0001F397\U0001F399-\U0001F39B\U0001F39E-\U0001F3F0\U0001F3F3-\U0001F3F5\U0001F3F7-\U0001F4FD\U0001F4FF-\U0001F53D\U0001F549-\U0001F54E\U0001F550-\U0001F567\U0001F56F\U0001F570\U0001F573-\U0001F57A\U0001F587\U0001F58A-\U0001F58D\U0001F590\U0001F595\U0001F596\U0001F5A4\U0001F5A5\U0001F5A8\U0001F5B1\U0001F5B2\U0001F5BC\U0001F5C2-\U0001F5C4\U0001F5D1-\U0001F5D3\U0001F5DC-\U0001F5DE\U0001F5E1\U0001F5E3\U0001F5E8\U0001F5EF\U0001F5F3\U0001F5FA-\U0001F64F\U0001F680-\U0001F6C5\U0001F6CB-\U0001F6D2\U0001F6D5\U0001F6E0-\U0001F6E5\U0001F6E9\U0001F6EB\U0001F6EC\U0001F6F0\U0001F6F3-\U0001F6FA\U0001F7E0-\U0001F7EB\U0001F90D-\U0001F93A\U0001F93C-\U0001F945\U0001F947-\U0001F971\U0001F973-\U0001F976\U0001F97A-\U0001F9A2\U0001F9A5-\U0001F9AA\U0001F9AE-\U0001F9CA\U0001F9CD-\U0001F9FF\U0001FA70-\U0001FA73\U0001FA78-\U0001FA7A\U0001FA80-\U0001FA82\U0001FA90-\U0001FA95]\uFE0F?|[\u261D\u26F9\u270A-\u270D\U0001F385\U0001F3C2-\U0001F3C4\U0001F3C7\U0001F3CA-\U0001F3CC\U0001F442\U0001F443\U0001F446-\U0001F450\U0001F466-\U0001F478\U0001F47C\U0001F481-\U0001F483\U0001F485-\U0001F487\U0001F48F\U0001F491\U0001F4AA\U0001F574\U0001F575\U0001F57A\U0001F590\U0001F595\U0001F596\U0001F645-\U0001F647\U0001F64B-\U0001F64F\U0001F6A3\U0001F6B4-\U0001F6B6\U0001F6C0\U0001F6CC\U0001F90F\U0001F918-\U0001F91F\U0001F926\U0001F930-\U0001F939\U0001F93C-\U0001F93E\U0001F9B5\U0001F9B6\U0001F9B8\U0001F9B9\U0001F9BB\U0001F9CD-\U0001F9CF\U0001F9D1-\U0001F9DD])'
word = r'([\w-]+)'
nonspace = r'([^\s])'
globreg = re.compile(discord_emo+'|'+discord_tag+'|'+url+'|'+uni_emo+'|'+word+'|'+nonspace)


def tokenize(msg: str) -> List[Token]:
	return [Token(next(token for token in match if token), match[0] != match[3]) for match in globreg.findall(msg)]


def ngrams(tokens: List[str], n: int) -> Iterator[Tuple]:
	return zip(*[tokens[i:] for i in range(n)])


def ngramslower(tokens: List[str], n) -> List[Union[Tuple, str]]:
	grams = tokens.copy()
	for i in range(2, n+1):
		grams += ngrams(tokens, i)
	return grams


discord_tag_group = re.compile(
	r'<@&([0-9]+)>|<@!?([0-9]+)>|<#([0-9]+)>'
)


def resolve_tags(ctx, wordcloud: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
	def repl_tag(match: re.match) -> str:
		if match[1]:
			# it's a role
			role = ctx.guild.get_role(int(match[1]))
			return '@'+role.name if role is not None else match[0]
		elif match[2]:
			# it's a member
			member = ctx.guild.get_member(int(match[2]))
			return '@'+member.name if member is not None else match[0]
		elif match[3]:
			# it's a channel
			channel = ctx.guild.get_channel(int(match[3]))
			return '#'+channel.name if channel is not None else match[0]
		return match[0]

	return [(discord_tag_group.sub(repl_tag, w), val) for (w, val) in wordcloud]
