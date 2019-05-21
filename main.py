from discord.ext.commands import Bot
from cog_model import ModelCog
from cog_management import ManagementCog
from cog_misc import MiscCog
bot = Bot(command_prefix=';')
bot.add_cog(ModelCog(bot))
bot.add_cog(ManagementCog(bot))
bot.add_cog(MiscCog(bot))


try:
	with open("token.txt", "r") as ftoken:
		token: str = ftoken.read().strip()
		bot.run(token)
except FileNotFoundError:
	print(
		"You're missing a token file, \n"
		"if you want to run this bot create a token.txt file at the root of this project\n"
		"and put your Discord Client ID in it.\nsee https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro")
