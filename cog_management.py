import discord.ext.commands as commands
from Management import ignored


class ManagementCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot: commands.Bot = bot

	def ignored_chan_msg(self, guild_id: int) -> str:
		ignoredchans = ignored.ignore_list(guild_id)
		if len(ignoredchans) == 0:
			return "There are currently no ignored channels for this guild."
		else:
			return "Ignored channels: " + ", ".join([f"<#{chanid}>" for chanid in ignoredchans]) \
				+ f"\nUse `{self.bot.command_prefix}listen <channel(s)>` to listen to channel(s) again."

	@commands.command()
	async def ignore(self, ctx):
		if ctx.message.author.guild_permissions.manage_channels:
			if len(ctx.message.channel_mentions) == 0:
				await ctx.channel.send(
					f"Command usage: `{self.bot.command_prefix}ignore <channel(s)>`, "
					f"it will make the bot ignore the channels when reading.\n{self.ignored_chan_msg(ctx.guild.id)}")
			else:
				for chan in ctx.message.channel_mentions:
					ignored.ignore(chan)
				await ctx.channel.send(self.ignored_chan_msg(ctx.guild.id))
		else:
			await ctx.channel.send(
				f"**{ctx.message.author.display_name}**, You need the **manage channel** permission to use this command.")

	@commands.command(aliases=["unignore"])
	async def listen(self, ctx):
		if ctx.message.author.guild_permissions.manage_channels:
			if len(ctx.message.channel_mentions) == 0:
				await ctx.channel.send(
					f"Command usage: `{self.bot.command_prefix}listen <channel(s)>`, "
					f"it will make the bot ignore the channels when reading.\n{self.ignored_chan_msg(ctx.guild.id)}")
			else:
				for chan in ctx.message.channel_mentions:
					ignored.unignore(chan)
				await ctx.channel.send(self.ignored_chan_msg(ctx.guild.id))
		else:
			await ctx.channel.send(
				f"**{ctx.message.author.display_name}**, You need the **manage channel** permission to use this command.")
