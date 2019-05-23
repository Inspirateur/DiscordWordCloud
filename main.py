from discord.ext.commands import Bot
from cog_cloud import Cloud
from cog_management import Management
from cog_misc import Misc
bot = Bot(command_prefix=';')
bot.add_cog(Cloud(bot))
bot.add_cog(Management(bot))
bot.add_cog(Misc(bot))


try:
	with open("token.txt", "r") as ftoken:
		token: str = ftoken.read().strip()
		bot.run(token)
except FileNotFoundError:
	print(
		"You're missing a token file, \n"
		"if you want to run this bot create a token.txt file at the root of this project\n"
		"and put your Discord Client ID in it.\nsee https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro")
