# DiscordWordCloud
A Python 3.9 discord bot that generates a word cloud (now with emojis !) for each discord user.

## How to run it
- Clone the project wherever you want
- Install Python 3.9 from https://www.python.org/
- Install the requirements listed in `requirements.txt` with `pip`
  - use `python -m pip install -r requirements.txt` at the root of the project
  - consult this guide if you need help with pip https://packaging.python.org/tutorials/installing-packages/
- add a `token.txt` file at the root of the project
- go to https://discordapp.com/developers/applications/ create your app, add a User Bot to it and paste its Client ID in `token.txt`
- you will also need to enable `SERVER MEMBERS INTENT` in the bot tab  
- invite the bot on your Discord Server https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot
- run `main.py` with Python 3.9

And it should run ! You might need to wait a bit while it reads the channels if you got many messages though.


If you got any questions about this project, feel free to DM `Inspi#8989` on Discord.

## Features
- `;cloud` to generate your word cloud, you can also tag someone in the command to generate their word cloud
- `;emojis` to get the custom emojis usage of the server

## Pictures

![sample image of my word cloud (french)](https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/cloud1.png)
![sample image of an english word cloud](https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/cloud1.png)
![sample image of ;emojis command](https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/emojis.png)

## Powered by:

- discord.py: https://github.com/Rapptz/discord.py
- WordCloud: https://github.com/amueller/word_cloud
- Twemoji: https://twemoji.twitter.com/
