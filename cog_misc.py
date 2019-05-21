import discord.ext.commands as commands
from cog_model import ModelCog


class MiscCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot

	@commands.command()
	async def word(self, ctx):
		modelcog: ModelCog = self.bot.get_cog("ModelCog")
		try:
			w: str = ctx.message.content.lower().split(" ")[1].strip()
			if w not in modelcog.model:
				await ctx.channel.send(f"'{w}' ? What's that :o ?")
			else:
				worduse = modelcog.model.word_use(w)
				resolved = []
				total: float = 0.0
				maxlen: int = 0
				for (userid, count) in worduse:
					user = ctx.guild.get_member(int(userid))
					if user is not None:
						resolved.append((user.name, count))
						total += count
						if len(user.name) > maxlen:
							maxlen = len(user.name)
					else:
						print(f"Couldn't resolve {userid}")
				print(w, resolved)
				txtlist = []
				for (user, count) in resolved:
					txtlist.append(user + (maxlen - len(user)) * ' ' + f" - {round(100.0 * count / total, 2)}%")
				txtstr = '\n'.join(txtlist)
				await ctx.channel.send(f"Top '**{w}**' users:\n```{txtstr}```")
		except KeyError:
			await ctx.channel.send(
				f"Command usage: `{self.bot.command_prefix}word <word>`, it will show you the top usage of <word>.")
