# DiscordWordCloud
A discord bot that generates a word cloud (now with emojis !) for each discord user.

The provided model used to generate the word cloud is dumb but fonctionnal, 
I encourage you to make your own by inheriting the `Model` class in `WordCloudModel/model.py` and importing it as `ModelClass` in `cog_model.py` ! 
(I personally use a custom model I unfortunately cannot disclose)

# How to run it
- Clone the project wherever you want
- Install the requirements listed in `requirements.txt` with `pip`
- add a `token.txt` file at the root of the project
- go to https://discordapp.com/developers/applications/ create your app, add a User Bot to it and paste its Client ID in `token.txt`
- invite your bot on a Discord Server https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot
- run the `main.py` with Python 3.5+!

If you wish to invite my version of this bot on your server or if you got any questions about this project, feel free to PM `Inspi#8989` on Discord !

# Features
For `everyone`:
- `;cloud (<user(s)>)` to generate your word cloud, you can also tag users to generate their clouds
- `;word <word>` to get a list of the top \<word> users in your server
- `;emojis` to get the podium of emojis in the guild

Requires `manage channel` permission:
- `;ignore <channel(s)>` to make make the bot ignore <channel(s)> while training the model
- `;listen <channel(s)>` to make make the bot listen to <channel(s)> while training the model 
(by defaults the bot read all the channel it has read access to)

Please note that this project is still in development, 
some features might still contain bugs or not be polished.

# Pictures

![sample image of a word cloud](https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/cloud_sample.png)
![sample image of a word top usage](https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/word_sample.png)

# Powered by:

- discord.py: https://github.com/Rapptz/discord.py
- WordCloud: https://github.com/amueller/word_cloud
- Twemoji: https://twemoji.twitter.com/
