from typing import List, Tuple
import discord.ext.commands as commands
from discord import TextChannel
from cog_cloud import Cloud


class Misc(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot

	@commands.command(brief="- Show the top usage of a given word")
	async def word(self, ctx, *args):
		if not isinstance(ctx.channel, TextChannel):
			await ctx.channel.send("Sorry, I can't answer this in DMs")
		elif len(args) > 0:
			print(
				f"{ctx.channel.guild.name}#{ctx.channel.name}: "
				f"{ctx.message.author.name}#{ctx.message.author.discriminator} has requested the word usage of "
				f"'{' '.join(args)}'"
			)
			modelcog: Cloud = self.bot.get_cog("Cloud")
			# get the words to look for
			words: str = " ".join(args[:modelcog.wordsn]).lower()
			if words not in modelcog.words[ctx.guild.id]:
				await ctx.channel.send(f"'{words}' ? What's that :o ?")
			else:
				# retrieve the word use
				worduse: List[Tuple[str, int]] = sorted(
					list(modelcog.words[ctx.guild.id][words].items()), key=lambda x: x[1], reverse=True
				)
				resolved = []
				total: float = 0.0
				maxlen: int = 0
				# resolve the userID to Members
				for (userid, count) in worduse:
					user = ctx.guild.get_member(int(userid))
					if user is not None:
						resolved.append((user.name, count))
						total += count
						if len(user.name) > maxlen:
							maxlen = len(user.name)
				# build the answer text
				txtlist = []
				for (user, count) in resolved:
					txtlist.append(user + (maxlen - len(user)) * ' ' + f" - {round(100.0 * count / total, 2)}%")
				txtstr = '\n'.join(txtlist)
				await ctx.channel.send(f"Top '**{words}**' users:\n```{txtstr}```")
		else:
			await ctx.channel.send(
				f"Command usage: `{self.bot.command_prefix}word <word(s)>`, it will show you the top usage of <word(s)>.")

	@commands.command(aliases=["emos"], brief="- Podium of the custom emojis for this server")
	async def emojis(self, ctx):
		if isinstance(ctx.channel, TextChannel):
			print(
				f"{ctx.channel.guild.name}#{ctx.channel.name}: "
				f"{ctx.message.author.name}#{ctx.message.author.discriminator} has requested the emoji podium."
			)
			modelcog: Cloud = self.bot.get_cog("Cloud")
			podium = []
			total = 0.0
			# for each emoji in the guild
			for emoji in ctx.guild.emojis:
				# get its usage and add it to the podium
				emo = str(emoji)
				if emo in modelcog.words[ctx.guild.id]:
					podium.append((emo, sum(modelcog.words[ctx.guild.id][emo].values())))
				else:
					podium.append((emo, 0))
				total += podium[-1][1]
			# sort the podium
			podium.sort(key=lambda x: x[1], reverse=True)
			# separate the top 10 from the rest
			top = podium[:10]
			other = podium[10:]
			# build the answer
			if total > 0:
				txtlist = []
				for (emoji, count) in top:
					txtlist.append(f"\t{emoji} {round(100.0*count/total, 2)}%")
				txtlist.append(" ".join([otheremo for (otheremo, count) in other]))
				await ctx.channel.send(f"Emoji Podium:\n"+"\n".join(txtlist))
			else:
				await ctx.channel.send("I didn't read any custom emojis yet :(")
		else:
			await ctx.channel.send("Sorry, I can't answer this in DMs")
